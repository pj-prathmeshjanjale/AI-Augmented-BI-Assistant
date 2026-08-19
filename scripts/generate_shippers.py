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

shippers = []

# Generate 10 shippers
for _ in range(10):
    shipper_name = fake.company()
    phone = fake.numerify("9#########")

    shippers.append((
        shipper_name,
        phone
    ))

query = """
INSERT INTO shippers
(shipper_name, phone)
VALUES (%s, %s)
"""

cursor.executemany(query, shippers)

conn.commit()

print(f"{cursor.rowcount} shippers inserted successfully!")

cursor.close()
conn.close()

















