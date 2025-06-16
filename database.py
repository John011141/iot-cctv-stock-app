# iot_cctv_stock/database.py

import sqlite3

DATABASE = 'stock.db'

def connect_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Makes rows behave like dictionaries for easy column access
    return conn

def init_db():
    # Connects to the database and creates tables if they don't exist
    with connect_db() as conn:
        cursor = conn.cursor()
        # Create 'products' table for master data of products
        # Changed 'model' column to 'image_url' to store paths to product images
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                mat_code TEXT UNIQUE NOT NULL,
                image_url TEXT  -- This column will now store the path to the product image
            )
        ''')
        # Create 'inventory_items' table for individual items with serial numbers
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                serial_number TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL, -- 'In Stock' or 'Issued'
                date_received TEXT NOT NULL,
                receiver_name TEXT NOT NULL,
                date_issued TEXT,
                issuer_name TEXT,
                job_id TEXT,
                FOREIGN KEY (product_id) REFERENCES products(id)
            )
        ''')
        conn.commit() # Commit the changes to the database
    print("Database initialized successfully.")

if __name__ == '__main__':
    # This block ensures that if database.py is run directly, it will initialize the database
    init_db()
