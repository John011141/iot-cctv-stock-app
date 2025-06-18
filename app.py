# app.py

import sqlite3
import os
import uuid
import click
import io
import csv
from flask import (
    Flask, render_template, request, redirect, url_for, flash, g, current_app, Response
)
from werkzeug.utils import secure_filename
import gspread

app = Flask(__name__)
# --- Configuration ---
app.config.from_mapping(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'a_very_long_and_complex_secret_key_for_your_app'),
    DATABASE=os.path.join(app.instance_path, 'inventory.db'),
    UPLOAD_FOLDER='static/images',
    GSHEET_NAME='My CCTV Stock' #! สำคัญ: แก้ไขชื่อชีตให้ตรงกับที่คุณสร้างไว้
)

# ตรวจสอบและสร้างโฟลเดอร์
try:
    os.makedirs(app.instance_path)
except OSError:
    pass
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


# --- Google Sheet Helper Function ---
def update_google_sheet():
    """
    ดึงข้อมูลทั้งหมดจาก SQLite แล้วเขียนทับลงใน Google Sheet
    """
    try:
        creds_path = os.path.join(current_app.instance_path, 'credentials.json')
        if not os.path.exists(creds_path):
            print("Google Sheets Warning: ไม่พบไฟล์ credentials.json ในโฟลเดอร์ instance")
            flash('ตั้งค่า Google Sheets ไม่สำเร็จ: ไม่พบไฟล์ credentials.json', 'warning')
            return

        gc = gspread.service_account(filename=creds_path)
        spreadsheet = gc.open(current_app.config['GSHEET_NAME'])
        db = get_db()
        
        # --- 1. อัปเดตชีตหลัก (ข้อมูลทั้งหมด) ---
        main_worksheet = spreadsheet.sheet1
        
        all_items = db.execute("""
            SELECT p.mat_code, ii.serial_number, p.name, ii.status,
                   ii.receiver_name, ii.date_received, ii.issuer_name, ii.date_issued
            FROM inventory_items ii JOIN products p ON ii.product_id = p.id
            ORDER BY 
                CASE WHEN ii.date_issued IS NULL OR ii.date_issued = '' THEN 1 ELSE 0 END,
                ii.date_issued ASC,                               
                p.mat_code,                                       
                ii.serial_number                                  
        """).fetchall()

        header = ["เลข Mat", "SN", "ชื่อสินค้า", "สถานะ", "ผู้รับผิดชอบ (รับเข้า)", "วันที่รับเข้า", "ช่างผู้เบิก", "วันที่เบิกจ่าย"]
        data_to_write = [header] + [[
            item['mat_code'], item['serial_number'], item['name'], item['status'],
            item['receiver_name'] or '-',
            str(item['date_received']) if item['date_received'] else '-',
            item['issuer_name'] or '-',
            str(item['date_issued']) if item['date_issued'] else '-'
        ] for item in all_items]
        
        main_worksheet.clear()
        main_worksheet.update('A1', data_to_write, value_input_option='USER_ENTERED')
        
        # --- 2. อัปเดตชีตสรุปยอดตามช่าง ---
        try:
            summary_worksheet = spreadsheet.worksheet("สรุปยอดตามช่าง")
        except gspread.exceptions.WorksheetNotFound:
            summary_worksheet = spreadsheet.add_worksheet(title="สรุปยอดตามช่าง", rows="100", cols="2")

        technician_summary = db.execute("""
            SELECT issuer_name, COUNT(id) AS item_count FROM inventory_items
            WHERE status = 'Issued' AND issuer_name IS NOT NULL AND issuer_name != ''
            GROUP BY issuer_name ORDER BY item_count DESC
        """).fetchall()

        summary_header = ["ชื่อช่างผู้เบิก", "จำนวนที่เบิกจ่าย (ชิ้น)"]
        summary_data_to_write = [summary_header] + [[item['issuer_name'], item['item_count']] for item in technician_summary]

        summary_worksheet.clear()
        summary_worksheet.update('A1', summary_data_to_write, value_input_option='USER_ENTERED')

        print("Successfully updated Google Sheet (Main and Summary).")
        flash('อัปเดตข้อมูลไปยัง Google Sheet เรียบร้อยแล้ว!', 'info')

    except Exception as e:
        print(f"Google Sheets Error: {e}")
        flash(f'เกิดข้อผิดพลาดในการเชื่อมต่อกับ Google Sheets: {e}', 'danger')


# --- Database Helpers ---
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    db.executescript("""
        DROP TABLE IF EXISTS inventory_items;
        DROP TABLE IF EXISTS products;

        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            mat_code TEXT NOT NULL UNIQUE,
            image_url TEXT
        );

        CREATE TABLE inventory_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            serial_number TEXT NOT NULL UNIQUE,
            status TEXT NOT NULL,
            date_received DATE,
            receiver_name TEXT,
            date_issued DATE,
            issuer_name TEXT,
            FOREIGN KEY (product_id) REFERENCES products (id)
        );
    """)

@app.cli.command('init-db')
def init_db_command():
    with app.app_context():
        init_db()
    click.echo('Initialized the database.')

# --- Utility ---
def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---
@app.route('/')
def index():
    return redirect(url_for('stock_overview'))

@app.route('/stock_overview')
def stock_overview():
    db = get_db()
    # Query เพื่อนับรวม 'ของเสีย' ในยอด 'เบิกจ่ายแล้ว' ถูกต้องแล้ว
    summary = db.execute("""
        SELECT p.name, p.mat_code, p.image_url, 
               COUNT(CASE WHEN ii.status = 'In Stock' THEN 1 END) AS in_stock_count, 
               COUNT(CASE WHEN ii.status = 'Issued' OR ii.status = 'ของเสีย' THEN 1 END) AS issued_count, 
               COUNT(ii.id) AS total_count 
        FROM products p 
        LEFT JOIN inventory_items ii ON p.id = ii.product_id 
        GROUP BY p.id 
        ORDER BY p.name
    """).fetchall()
    
    # ==================== START: แก้ไขจุดนี้ ====================
    # แก้ไข ORDER BY ให้เรียงตามวันที่เบิกจ่าย (date_issued) เป็นหลัก
    all_items = db.execute("""
        SELECT ii.id, p.mat_code, ii.serial_number, p.name, ii.status, 
               ii.receiver_name, ii.date_issued, ii.issuer_name 
        FROM inventory_items ii JOIN products p ON ii.product_id = p.id 
        ORDER BY 
            CASE WHEN ii.date_issued IS NULL OR ii.date_issued = '' THEN 1 ELSE 0 END, 
            ii.date_issued ASC,
            p.mat_code ASC,
            ii.serial_number ASC
    """).fetchall()
    # ===================== END: แก้ไขจุดนี้ =====================
    
    technician_summary = db.execute("""
        SELECT issuer_name, COUNT(id) AS item_count FROM inventory_items
        WHERE status = 'Issued' AND issuer_name IS NOT NULL AND issuer_name != ''
        GROUP BY issuer_name ORDER BY item_count DESC
    """).fetchall()
    
    return render_template('stock_overview.html', 
                           summary=summary, 
                           all_items=all_items,
                           technician_summary=technician_summary)

@app.route('/export_csv')
def export_csv():
    db = get_db()
    # For CSV export, let's keep the original sorting unless specified otherwise
    all_items = db.execute("""
        SELECT p.mat_code, ii.serial_number, p.name, ii.status,
               ii.receiver_name, ii.date_received, ii.issuer_name, ii.date_issued
        FROM inventory_items ii JOIN products p ON ii.product_id = p.id
        ORDER BY p.mat_code, ii.serial_number
    """).fetchall()

    si = io.StringIO()
    cw = csv.writer(si)
    header = ["เลข Mat", "SN", "ชื่อสินค้า", "สถานะ", "ผู้รับผิดชอบ (รับเข้า)", "วันที่รับเข้า", "ช่างผู้เบิก", "วันที่เบิกจ่าย"]
    cw.writerow(header)
    for item in all_items:
        row = [
            f"=\"{item['mat_code']}\"",
            f"=\"{item['serial_number']}\"",
            item['name'],
            item['status'],
            item['receiver_name'] or '', 
            str(item['date_received']) if item['date_received'] else '',
            item['issuer_name'] or '', 
            str(item['date_issued']) if item['date_issued'] else ''
        ]
        cw.writerow(row)

    output_string = si.getvalue()
    output_bytes = output_string.encode('utf-8-sig')
    
    return Response(
        output_bytes,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=stock_export.csv"}
    )

@app.route('/stock_in', methods=['GET', 'POST'])
def stock_in():
    db = get_db()
    if request.method == 'POST':
        try:
            product_id = request.form['product_id']
            receiver_name = request.form['receiver_name']
            date_received = request.form['date_received']
            serial_numbers_raw = request.form['serial_numbers_bulk']
            serial_numbers = [sn.strip() for sn in serial_numbers_raw.splitlines() if sn.strip()]

            if not serial_numbers:
                flash('กรุณากรอก Serial Number อย่างน้อยหนึ่งหมายเลข', 'error')
                return redirect(url_for('stock_in'))

            cursor = db.cursor()
            received_count = 0
            for sn in serial_numbers:
                existing_sn = cursor.execute("SELECT id FROM inventory_items WHERE serial_number = ?", (sn,)).fetchone()
                if existing_sn:
                    flash(f'Serial Number "{sn}" มีอยู่ในระบบแล้ว', 'warning')
                    continue
                cursor.execute(
                    "INSERT INTO inventory_items (product_id, serial_number, status, date_received, receiver_name) VALUES (?, ?, ?, ?, ?)",
                    (product_id, sn, 'In Stock', date_received, receiver_name)
                )
                received_count += 1
            if received_count > 0:
                db.commit()
                flash(f'รับสินค้าเข้า {received_count} ชิ้นเรียบร้อยแล้ว!', 'success')
                update_google_sheet()
        except sqlite3.Error as e:
            db.rollback()
            flash(f'เกิดข้อผิดพลาดในการบันทึกข้อมูล: {e}', 'error')
        return redirect(url_for('stock_in'))

    products = db.execute("SELECT id, name, mat_code, image_url FROM products ORDER BY name").fetchall()
    return render_template('stock_in.html', products=products)

@app.route('/stock_out', methods=['GET', 'POST'])
def stock_out():
    db = get_db()
    if request.method == 'POST':
        try:
            mat_code = request.form['mat_code'].strip()
            serial_numbers_raw = request.form['serial_numbers_bulk']
            serial_numbers_to_issue = [sn.strip() for sn in serial_numbers_raw.splitlines() if sn.strip()]
            date_issued = request.form['date_issued']
            issuer_name = request.form['issuer_name']

            if not serial_numbers_to_issue:
                flash('กรุณากรอก Serial Number ที่ต้องการเบิกจ่าย', 'error')
                return redirect(url_for('stock_out'))
            cursor = db.cursor()
            issued_count = 0
            for sn in serial_numbers_to_issue:
                item_query = "SELECT ii.id FROM inventory_items ii JOIN products p ON ii.product_id = p.id WHERE ii.serial_number = ? AND ii.status = 'In Stock' AND p.mat_code = ?"
                item = cursor.execute(item_query, (sn, mat_code)).fetchone()
                if item:
                    cursor.execute("UPDATE inventory_items SET status = 'Issued', date_issued = ?, issuer_name = ? WHERE id = ?", (date_issued, issuer_name, item['id']))
                    issued_count += 1
                else:
                    flash(f'Serial Number "{sn}" ไม่พบ, ไม่ตรงกับ Mat Code, หรือไม่ได้อยู่ในสถานะ "In Stock"', 'warning')
            if issued_count > 0:
                db.commit()
                flash(f'เบิกจ่ายอุปกรณ์ {issued_count} ชิ้นเรียบร้อยแล้ว!', 'success')
                update_google_sheet()
            else:
                flash('ไม่สามารถเบิกจ่ายอุปกรณ์ได้ กรุณาตรวจสอบข้อมูล', 'error')
        except sqlite3.Error as e:
            db.rollback()
            flash(f'เกิดข้อผิดพลาดในการเบิกจ่าย: {e}', 'error')
        return redirect(url_for('stock_out'))
    
    products_in_stock = db.execute("SELECT DISTINCT p.id, p.name, p.mat_code FROM products p JOIN inventory_items ii ON p.id = ii.product_id WHERE ii.status = 'In Stock' ORDER BY p.name").fetchall()
    return render_template('stock_out.html', products=products_in_stock)

# --- START: โค้ดสำหรับรับคืนสินค้า (เวอร์ชันอัปเดตตาม Logic ล่าสุด) ---
@app.route('/stock_return', methods=['GET', 'POST'])
def stock_return():
    db = get_db()
    if request.method == 'POST':
        try:
            # item_id และ action จะถูกส่งมาจากฟอร์มในหน้า stock_return.html
            item_id = request.form['item_id']
            action = request.form.get('action') 

            if action == 'return_to_stock':
                # คืนของดี: เปลี่ยนสถานะเป็น In Stock และล้างข้อมูลวันที่/ผู้เบิก
                db.execute(
                    """UPDATE inventory_items 
                       SET status = 'In Stock', date_issued = NULL, issuer_name = NULL 
                       WHERE id = ?""",
                    (item_id,)
                )
                db.commit()
                flash('รับคืนสินค้า (สภาพดี) เข้าสต็อกเรียบร้อยแล้ว!', 'success')

            elif action == 'mark_defective':
                # คืนของเสีย: เปลี่ยนสถานะเป็น 'ของเสีย' และเก็บข้อมูลผู้เบิก/วันที่ไว้
                db.execute(
                    "UPDATE inventory_items SET status = 'ของเสีย' WHERE id = ?",
                    (item_id,)
                )
                db.commit()
                flash('บันทึกสินค้าเป็นของเสียเรียบร้อยแล้ว!', 'warning')
            
            else:
                flash('การกระทำไม่ถูกต้อง', 'danger')

            # อัปเดต Google Sheet หลังจากทำรายการเสร็จ
            update_google_sheet()

        except sqlite3.Error as e:
            db.rollback()
            flash(f'เกิดข้อผิดพลาดในการรับคืนสินค้า: {e}', 'error')
        
        return redirect(url_for('stock_return'))

    # สำหรับ GET request, แสดงรายการทั้งหมดที่ถูกเบิกจ่ายไปเพื่อรอการคืน
    issued_items = db.execute("""
        SELECT ii.id, ii.serial_number, p.name, ii.issuer_name, ii.date_issued
        FROM inventory_items ii JOIN products p ON ii.product_id = p.id
        WHERE ii.status = 'Issued'
        ORDER BY ii.date_issued DESC
    """).fetchall()
    return render_template('stock_return.html', items=issued_items)
# --- END: โค้ดสำหรับรับคืนสินค้า ---

@app.route('/clear_all_stock', methods=['POST'])
def clear_all_stock():
    db = get_db()
    try:
        db.execute("DELETE FROM inventory_items")
        db.commit()
        flash('ล้างสต็อกทั้งหมดเรียบร้อยแล้ว!', 'success')
        update_google_sheet()
    except sqlite3.Error as e:
        db.rollback()
        flash(f'เกิดข้อผิดพลาดในการล้างสต็อก: {e}', 'error')
    return redirect(url_for('stock_overview'))

@app.route('/manage_products', methods=['GET', 'POST'])
def manage_products():
    db = get_db()
    if request.method == 'POST':
        action = request.form.get('action')
        try:
            if action == 'add' or action == 'edit':
                name = request.form['name']
                mat_code = request.form['mat_code']
                image_url = ''
                if 'product_image' in request.files:
                    file = request.files['product_image']
                    if file and allowed_file(file.filename):
                        filename = secure_filename(f"{uuid.uuid4()}{os.path.splitext(file.filename)[1]}")
                        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                        image_url = url_for('static', filename=f'images/{filename}')
                    elif file.filename != '':
                        flash('รูปแบบไฟล์รูปภาพไม่ถูกต้อง (อนุญาต: png, jpg, jpeg, gif)', 'error')
                        return redirect(url_for('manage_products'))
                if action == 'add':
                    db.execute("INSERT INTO products (name, mat_code, image_url) VALUES (?, ?, ?)", (name, mat_code, image_url))
                    flash('เพิ่มข้อมูลสินค้าหลักสำเร็จ!', 'success')
                elif action == 'edit':
                    product_id = request.form.get('product_id')
                    if not image_url:
                        product = db.execute("SELECT image_url FROM products WHERE id = ?", (product_id,)).fetchone()
                        if product: image_url = product['image_url']
                    db.execute("UPDATE products SET name = ?, mat_code = ?, image_url = ? WHERE id = ?", (name, mat_code, image_url, product_id))
                    flash('แก้ไขข้อมูลสินค้าหลักสำเร็จ!', 'success')
            elif action == 'delete':
                product_id = request.form.get('product_id')
                item_count = db.execute("SELECT COUNT(*) FROM inventory_items WHERE product_id = ?", (product_id,)).fetchone()[0]
                if item_count > 0:
                    flash('ไม่สามารถลบได้ เนื่องจากมี Serial Number ที่เชื่อมโยงกับสินค้านี้ในสต็อก', 'error')
                else:
                    product = db.execute("SELECT image_url FROM products WHERE id = ?", (product_id,)).fetchone()
                    if product and product['image_url']:
                        try:
                            filename = os.path.basename(product['image_url'])
                            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                            if os.path.exists(image_path): os.remove(image_path)
                        except Exception as file_error:
                            flash(f'ไม่สามารถลบไฟล์รูปภาพได้: {file_error}', 'warning')
                    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
                    flash('ลบข้อมูลสินค้าหลักสำเร็จ!', 'success')
            db.commit()
        except sqlite3.IntegrityError:
            db.rollback()
            flash('เลข Mat Code นี้มีอยู่แล้วในระบบ กรุณาใช้เลขอื่น', 'error')
        except Exception as e:
            db.rollback()
            flash(f'เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}', 'error')
        return redirect(url_for('manage_products'))
    products = db.execute("SELECT id, name, mat_code, image_url FROM products ORDER BY name").fetchall()
    return render_template('manage_products.html', products=products)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
