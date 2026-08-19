import mysql.connector
from faker import Faker

fake = Faker("en_IN")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="business_db"
)

cursor = conn.cursor()

# Get existing category IDs
cursor.execute("SELECT category_id FROM categories")
category_ids = [row[0] for row in cursor.fetchall()]

# Get existing supplier IDs
cursor.execute("SELECT supplier_id FROM suppliers")
supplier_ids = [row[0] for row in cursor.fetchall()]

if not category_ids:
    print("No categories found. Please insert categories first.")
    cursor.close()
    conn.close()
    exit()

if not supplier_ids:
    print("No suppliers found. Please insert suppliers first.")
    cursor.close()
    conn.close()
    exit()

products = []

# Generate 500 products
for i in range(500):

    product_name = f"{fake.word().title()} {fake.word().title()} {i + 1}"

    category_id = fake.random_element(category_ids)

    supplier_id = fake.random_element(supplier_ids)

    unit_price = round(
        fake.random_int(min=100, max=100000),
        2
    )

    stock_quantity = fake.random_int(
        min=0,
        max=500
    )

    created_at = fake.date_between(
        start_date="-3y",
        end_date="today"
    )

    products.append((
        product_name,
        category_id,
        supplier_id,
        unit_price,
        stock_quantity,
        created_at
    ))

query = """
INSERT INTO products
(
    product_name,
    category_id,
    supplier_id,
    unit_price,
    stock_quantity,
    created_at
)
VALUES (%s, %s, %s, %s, %s, %s)
"""

cursor.executemany(query, products)

conn.commit()

print(f"{cursor.rowcount} products inserted successfully!")

cursor.close()
conn.close()