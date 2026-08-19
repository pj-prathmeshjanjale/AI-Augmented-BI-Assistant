import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",      # Change if your MySQL has a password
    database="business_db"
)

cursor = conn.cursor()

# Region data
regions = [
    ("North", "Amit Sharma"),
    ("South", "Priya Nair"),
    ("East", "Rahul Verma"),
    ("West", "Sneha Patel"),
    ("Central", "Vikram Singh")
]

# Insert data
query = """
INSERT INTO regions (region_name, manager_name)
VALUES (%s, %s)
"""

cursor.executemany(query, regions)

# Save changes
conn.commit()

print(f"{cursor.rowcount} regions inserted successfully!")

cursor.close()
conn.close()