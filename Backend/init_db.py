import sqlite3
import json
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = BASE_DIR / "backend" / "database.db"

PRODUCTS_FILE = DATA_DIR / "products.json"

# Load product data
with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

# Create database
connection = sqlite3.connect(DB_PATH)
cursor = connection.cursor()

# Create products table
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    brand TEXT NOT NULL,
    category TEXT NOT NULL,
    image TEXT NOT NULL
)
""")

# Clear existing product records
cursor.execute("DELETE FROM products")

# Insert 65 products
for product in products:
    cursor.execute("""
        INSERT INTO products
        (id, name, brand, category, image)
        VALUES (?, ?, ?, ?, ?)
    """, (
        product["id"],
        product["name"],
        product["brand"],
        product["category"],
        product["image"]
    ))

connection.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM products")
count = cursor.fetchone()[0]

connection.close()

print("=" * 50)
print("DATABASE INITIALIZED")
print("=" * 50)
print(f"Products inserted: {count}")
print(f"Database location: {DB_PATH}")
print("=" * 50)