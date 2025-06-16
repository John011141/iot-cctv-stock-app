#!/usr/bin/env bash
# exit on error
set -o errexit

# ติดตั้ง Library ทั้งหมด
pip install -r requirements.txt

# สร้างฐานข้อมูล (ใช้คำสั่ง flask init-db ที่เรามีอยู่แล้ว)
export FLASK_APP=app.py
flask init-db
