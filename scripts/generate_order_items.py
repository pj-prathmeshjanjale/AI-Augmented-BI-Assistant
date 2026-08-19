import mysql.connector
import random

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="business_db"
)

cursor = conn.cursor()

# Get product IDs and prices
cursor.execute("""
    SELECT product_id, unit_price
    FROM products
""")

products = cursor.fetchall()

# Get order IDs
cursor.execute("""
    SELECT order_id
    FROM orders
""")

order_ids = [row[0] for row in cursor.fetchall()]

if not products:
    print("No products found.")
    cursor.close()
    conn.close()
    exit()

if not order_ids:
    print("No orders found.")
    cursor.close()
    conn.close()
    exit()

# Generate 50,000 order items
order_items = []

for _ in range(50000):

    order_id = random.choice(order_ids)

    product_id, product_price = random.choice(products)

    quantity = random.randint(1, 5)

    unit_price = product_price

    order_items.append((
        order_id,
        product_id,
        quantity,
        unit_price
    ))

query = """
INSERT INTO order_items
(
    order_id,
    product_id,
    quantity,
    unit_price
)
VALUES (%s, %s, %s, %s)
"""

# Insert in batches to avoid max_allowed_packet error
batch_size = 1000

for i in range(0, len(order_items), batch_size):

    batch = order_items[i:i + batch_size]

    cursor.executemany(query, batch)

    conn.commit()

    print(
        f"Inserted {min(i + batch_size, len(order_items))} "
        f"/ {len(order_items)} order items"
    )

print("50000 order items inserted successfully!")

cursor.close()
conn.close()