import os
import sqlite3

DEFAULT_DB_PATH = "default_business.db"


def seed_default_business_db():
    """Creates and populates default_business.db for cloud online execution of business_db queries."""
    conn = sqlite3.connect(DEFAULT_DB_PATH)
    cursor = conn.cursor()

    # 1. Regions
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS regions (
            region_id INTEGER PRIMARY KEY,
            region_name TEXT,
            manager_name TEXT
        );
    """)

    # 2. Categories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT,
            description TEXT
        );
    """)

    # 3. Suppliers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INTEGER PRIMARY KEY,
            supplier_name TEXT,
            contact_name TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            country TEXT
        );
    """)

    # 4. Shippers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shippers (
            shipper_id INTEGER PRIMARY KEY,
            shipper_name TEXT,
            phone TEXT
        );
    """)

    # 5. Customers
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            gender TEXT,
            email TEXT,
            phone TEXT,
            city TEXT,
            state TEXT,
            country TEXT,
            registration_date TEXT,
            region_id INTEGER
        );
    """)

    # 6. Employees
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            email TEXT,
            phone TEXT,
            department TEXT,
            hire_date TEXT,
            salary REAL
        );
    """)

    # 7. Products
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            product_name TEXT,
            category_id INTEGER,
            supplier_id INTEGER,
            unit_price REAL,
            stock_quantity INTEGER,
            created_at TEXT
        );
    """)

    # 8. Orders
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY,
            customer_id INTEGER,
            order_date TEXT,
            order_status TEXT,
            total_amount REAL,
            shipper_id INTEGER
        );
    """)

    # 9. Order Items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            unit_price REAL
        );
    """)

    # 10. Payments
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            payment_id INTEGER PRIMARY KEY,
            order_id INTEGER,
            payment_date TEXT,
            payment_method TEXT,
            payment_status TEXT,
            amount REAL
        );
    """)

    # Seed Sample Data if tables are empty
    cursor.execute("SELECT COUNT(*) FROM regions;")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("INSERT INTO regions VALUES (?, ?, ?)", [
            (1, "North America", "Sarah Jenkins"),
            (2, "Europe Central", "Marco Rossi"),
            (3, "Asia Pacific", "Kenji Sato"),
            (4, "Latin America", "Carlos Silva"),
            (5, "Middle East", "Tariq Al-Mansoor")
        ])

        cursor.executemany("INSERT INTO categories VALUES (?, ?, ?)", [
            (1, "Electronics", "Gadgets, Devices, and Hardware Accessories"),
            (2, "Furniture", "Office Desks, Chairs, and Storage Units"),
            (3, "Appliances", "Home and Kitchen Machinery"),
            (4, "Software", "Enterprise Subscriptions and SaaS Tools"),
            (5, "Stationery", "Paper, Pens, and Office Supplies")
        ])

        cursor.executemany("INSERT INTO suppliers VALUES (?, ?, ?, ?, ?, ?, ?)", [
            (1, "TechCorp Supplies", "Alex Mercer", "contact@techcorp.com", "+1-555-0192", "San Jose", "USA"),
            (2, "Global Office Furniture", "Elena Rostova", "sales@globalfurniture.com", "+49-30-12345", "Berlin", "Germany"),
            (3, "Nippon Components", "Yuki Tanaka", "info@nipponcomp.jp", "+81-3-5555", "Tokyo", "Japan"),
            (4, "EuroTech Solutions", "Jean Dupont", "contact@eurotech.fr", "+33-1-4000", "Paris", "France"),
            (5, "Apex Industrial Supplies", "David Miller", "sales@apexind.com", "+1-800-555", "Chicago", "USA")
        ])

        cursor.executemany("INSERT INTO shippers VALUES (?, ?, ?)", [
            (1, "Express Logistics", "+1-800-EXPRESS"),
            (2, "Global Freight Lines", "+1-800-FREIGHT"),
            (3, "Speedy Ship Corp", "+44-20-SPEEDY"),
            (4, "Pacific Air Courier", "+81-3-PACIFIC"),
            (5, "EuroTrans Transport", "+49-89-EURO")
        ])

        cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            (101, "John", "Doe", "Male", "john.doe@example.com", "+1-555-0101", "New York", "NY", "USA", "2024-01-15", 1),
            (102, "Emma", "Watson", "Female", "emma.w@example.com", "+44-20-0102", "London", "Greater London", "UK", "2024-02-10", 2),
            (103, "Akira", "Tanaka", "Male", "akira.t@example.com", "+81-3-0103", "Tokyo", "Kanto", "Japan", "2024-03-05", 3),
            (104, "Maria", "Garcia", "Female", "maria.g@example.com", "+34-91-0104", "Madrid", "Madrid", "Spain", "2024-03-20", 2),
            (105, "Liam", "Smith", "Male", "liam.s@example.com", "+1-555-0105", "Toronto", "Ontario", "Canada", "2024-04-12", 1),
            (106, "Sophie", "Martin", "Female", "sophie.m@example.com", "+33-1-0106", "Paris", "Ile-de-France", "France", "2024-05-01", 2),
            (107, "Wei", "Zhang", "Male", "wei.z@example.com", "+86-10-0107", "Beijing", "Beijing", "China", "2024-05-18", 3),
            (108, "Lucia", "Santos", "Female", "lucia.s@example.com", "+55-11-0108", "Sao Paulo", "SP", "Brazil", "2024-06-02", 4),
            (109, "Ahmed", "Hassan", "Male", "ahmed.h@example.com", "+971-4-0109", "Dubai", "Dubai", "UAE", "2024-06-15", 5),
            (110, "Olivia", "Brown", "Female", "olivia.b@example.com", "+1-555-0110", "Chicago", "IL", "USA", "2024-07-01", 1)
        ])

        cursor.executemany("INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
            (201, "Alice", "Johnson", "alice.j@company.com", "+1-555-0201", "Sales", "2022-03-15", 85000.00),
            (202, "Bob", "Smith", "bob.s@company.com", "+1-555-0202", "Sales", "2022-06-01", 78000.00),
            (203, "Charlie", "Davis", "charlie.d@company.com", "+1-555-0203", "Marketing", "2023-01-10", 72000.00),
            (204, "Diana", "Prince", "diana.p@company.com", "+1-555-0204", "Engineering", "2021-11-20", 110000.00),
            (205, "Ethan", "Hunt", "ethan.h@company.com", "+1-555-0205", "Logistics", "2023-04-05", 65000.00)
        ])

        cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?, ?, ?, ?)", [
            (1, "UltraBook Pro 15", 1, 1, 1299.99, 45, "2024-01-10"),
            (2, "4K Curved Monitor", 1, 1, 499.50, 80, "2024-01-12"),
            (3, "Ergonomic Mesh Chair", 2, 2, 349.00, 120, "2024-01-15"),
            (4, "Standing Office Desk", 2, 2, 599.00, 35, "2024-01-20"),
            (5, "Smart Espresso Maker", 3, 3, 249.99, 60, "2024-02-01"),
            (6, "Wireless Noise-Canceling Headphones", 1, 3, 199.99, 150, "2024-02-05"),
            (7, "Enterprise BI Suite Sub", 4, 4, 899.00, 999, "2024-02-10"),
            (8, "Mechanical Keyboard RGB", 1, 1, 129.99, 200, "2024-02-15"),
            (9, "Laserjet Pro Printer", 1, 5, 399.00, 40, "2024-03-01"),
            (10, "Premium Leather Notebook Set", 5, 5, 29.99, 500, "2024-03-05")
        ])

        cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?, ?)", [
            (1001, 101, "2024-06-01", "Completed", 1799.49, 1),
            (1002, 102, "2024-06-03", "Completed", 349.00, 2),
            (1003, 103, "2024-06-05", "Completed", 1299.99, 3),
            (1004, 104, "2024-06-10", "Shipped", 848.99, 2),
            (1005, 105, "2024-06-15", "Completed", 599.00, 1),
            (1006, 106, "2024-06-18", "Completed", 199.99, 5),
            (1007, 107, "2024-06-22", "Completed", 899.00, 4),
            (1008, 108, "2024-06-25", "Pending", 249.99, 1),
            (1009, 109, "2024-06-28", "Completed", 1429.98, 5),
            (1010, 110, "2024-07-01", "Completed", 399.00, 1),
            (1011, 101, "2024-07-03", "Completed", 499.50, 1),
            (1012, 102, "2024-07-05", "Completed", 129.99, 2),
            (1013, 105, "2024-07-08", "Shipped", 1299.99, 3),
            (1014, 107, "2024-07-10", "Completed", 349.00, 4),
            (1015, 109, "2024-07-12", "Completed", 599.00, 5)
        ])

        cursor.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", [
            (1, 1001, 1, 1, 1299.99),
            (2, 1001, 2, 1, 499.50),
            (3, 1002, 3, 1, 349.00),
            (4, 1003, 1, 1, 1299.99),
            (5, 1004, 3, 1, 349.00),
            (6, 1004, 2, 1, 499.99),
            (7, 1005, 4, 1, 599.00),
            (8, 1006, 6, 1, 199.99),
            (9, 1007, 7, 1, 899.00),
            (10, 1008, 5, 1, 249.99),
            (11, 1009, 1, 1, 1299.99),
            (12, 1009, 8, 1, 129.99),
            (13, 1010, 9, 1, 399.00),
            (14, 1011, 2, 1, 499.50),
            (15, 1012, 8, 1, 129.99),
            (16, 1013, 1, 1, 1299.99),
            (17, 1014, 3, 1, 349.00),
            (18, 1015, 4, 1, 599.00)
        ])

        cursor.executemany("INSERT INTO payments VALUES (?, ?, ?, ?, ?, ?)", [
            (1, 1001, "2024-06-01", "Credit Card", "Completed", 1799.49),
            (2, 1002, "2024-06-03", "PayPal", "Completed", 349.00),
            (3, 1003, "2024-06-05", "Wire Transfer", "Completed", 1299.99),
            (4, 1004, "2024-06-10", "Credit Card", "Completed", 848.99),
            (5, 1005, "2024-06-15", "Credit Card", "Completed", 599.00),
            (6, 1006, "2024-06-18", "Apple Pay", "Completed", 199.99),
            (7, 1007, "2024-06-22", "Corporate Account", "Completed", 899.00),
            (8, 1009, "2024-06-28", "Credit Card", "Completed", 1429.98),
            (9, 1010, "2024-07-01", "Credit Card", "Completed", 399.00),
            (10, 1011, "2024-07-03", "PayPal", "Completed", 499.50)
        ])

    conn.commit()
    conn.close()
    print("Pre-seeded default_business.db successfully!")


if __name__ == "__main__":
    seed_default_business_db()
