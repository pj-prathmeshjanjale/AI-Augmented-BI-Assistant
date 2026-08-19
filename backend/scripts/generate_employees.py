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

employees = []

departments = [
    "Sales",
    "Marketing",
    "Finance",
    "Operations",
    "IT",
    "Human Resources"
]

# Generate 50 employees
for _ in range(50):

    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    phone = fake.numerify("9#########")
    department = fake.random_element(departments)
    hire_date = fake.date_between(
        start_date="-5y",
        end_date="today"
    )
    salary = round(
        fake.random_int(min=20000, max=100000),
        2
    )

    employees.append((
        first_name,
        last_name,
        email,
        phone,
        department,
        hire_date,
        salary
    ))

query = """
INSERT INTO employees
(first_name, last_name, email, phone, department, hire_date, salary)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

cursor.executemany(query, employees)

conn.commit()

print(f"{cursor.rowcount} employees inserted successfully!")

cursor.close()
conn.close()