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

suppliers = []

for _ in range(50):
    supplier_name = fake.company()
    contact_name = fake.name()
    email = fake.unique.email()
    phone = fake.numerify("9#########")
    city = fake.city()
    country = "India"

    suppliers.append((
        supplier_name,
        contact_name,
        email,
        phone,
        city,
        country
    ))

query = """
INSERT INTO suppliers
(supplier_name, contact_name, email, phone, city, country)
VALUES (%s, %s, %s, %s, %s, %s)
"""

cursor.executemany(query, suppliers)

conn.commit()

print(f"{cursor.rowcount} suppliers inserted successfully!")

cursor.close()
conn.close()
