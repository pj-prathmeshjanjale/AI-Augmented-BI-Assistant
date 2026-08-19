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

# Get existing region IDs
cursor.execute("SELECT region_id FROM regions")
region_ids = [row[0] for row in cursor.fetchall()]

if not region_ids:
    print("No regions found. Please insert regions first.")
    cursor.close()
    conn.close()
    exit()

customers = []

# Generate 5,000 customers
for _ in range(5000):

    first_name = fake.first_name()
    last_name = fake.last_name()

    gender = fake.random_element(
        ["Male", "Female", "Other"]
    )

    email = fake.unique.email()

    phone = fake.numerify("9#########")

    city = fake.city()
    state = fake.state()
    country = "India"

    registration_date = fake.date_between(
        start_date="-5y",
        end_date="today"
    )

    region_id = fake.random_element(region_ids)

    customers.append((
        first_name,
        last_name,
        gender,
        email,
        phone,
        city,
        state,
        country,
        registration_date,
        region_id
    ))

query = """
INSERT INTO customers
(
    first_name,
    last_name,
    gender,
    email,
    phone,
    city,
    state,
    country,
    registration_date,
    region_id
)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

cursor.executemany(query, customers)

conn.commit()

print(f"{cursor.rowcount} customers inserted successfully!")

cursor.close()
conn.close()