import mysql.connector

# Connect to MySQL
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="business_db"
)

cursor = conn.cursor()

categories = [
    ("Electronics", "Electronic gadgets and devices"),
    ("Clothing", "Men's and Women's clothing"),
    ("Home & Kitchen", "Home appliances and kitchen essentials"),
    ("Sports", "Sports equipment and accessories"),
    ("Beauty", "Beauty and skincare products"),
    ("Books", "Books and educational material"),
    ("Toys", "Toys and games for children"),
    ("Grocery", "Daily grocery items"),
    ("Furniture", "Home and office furniture"),
    ("Automotive", "Vehicle parts and accessories"),
    ("Mobile Accessories", "Phone cases, chargers, etc."),
    ("Computers & Laptops", "Computers and related accessories"),
    ("Health & Personal Care", "Healthcare products"),
    ("Watches", "Wrist watches and smartwatches"),
    ("Footwear", "Shoes and sandals"),
    ("Jewelry", "Gold, silver and fashion jewelry"),
    ("Office Supplies", "Office stationery and supplies"),
    ("Pet Supplies", "Food and accessories for pets"),
    ("Baby Products", "Products for babies and infants"),
    ("Musical Instruments", "Guitars, keyboards and more")
]

query = """
INSERT INTO categories (category_name, description)
VALUES (%s, %s)
"""

cursor.executemany(query, categories)

conn.commit()

print(f"{cursor.rowcount} categories inserted successfully!")

cursor.close()
conn.close()