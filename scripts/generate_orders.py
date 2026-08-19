import mysql.connector
from faker import Faker
import random

fake = Faker("en_IN")

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="business_db"
)

cursor = conn.cursor()

# Get existing customer IDs
cursor.execute("SELECT customer_id FROM customers")
customer_ids = [row[0] for row in cursor.fetchall()]

# Get existing shipper IDs
cursor.execute("SELECT shipper_id FROM shippers")
shipper_ids = [row[0] for row in cursor.fetchall()]

if not customer_ids:
    print("No customers found.")
    cursor.close()
    conn.close()
    exit()

if not shipper_ids:
    print("No shippers found.")
    cursor.close()
    conn.close()
    exit()

orders = []

statuses = [
    "Pending",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled"
]

# Generate 20,000 orders
for _ in range(20000):

    customer_id = random.choice(customer_ids)

    order_date = fake.date_between(
        start_date="-2y",
        end_date="today"
    )

    order_status = random.choice(statuses)

    # Temporary amount.
    # We will recalculate this from order_items later.
    total_amount = round(
        random.uniform(500, 50000),
        2
    )

    shipper_id = random.choice(shipper_ids)

    orders.append((
        customer_id,
        order_date,
        order_status,
        total_amount,
        shipper_id
    ))

query = """
INSERT INTO orders
(
    customer_id,
    order_date,
    order_status,
    total_amount,
    shipper_id
)
VALUES (%s, %s, %s, %s, %s)
"""

cursor.executemany(query, orders)

conn.commit()

print(f"{cursor.rowcount} orders inserted successfully!")

cursor.close()
conn.close()