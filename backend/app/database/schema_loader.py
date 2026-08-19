import os
import sqlite3
from app.database.connection import get_connection


MYSQL_SCHEMA_FALLBACK = {
    "categories": [
        {"column": "category_id", "type": "int"},
        {"column": "category_name", "type": "varchar"},
        {"column": "description", "type": "text"}
    ],
    "customers": [
        {"column": "customer_id", "type": "int"},
        {"column": "first_name", "type": "varchar"},
        {"column": "last_name", "type": "varchar"},
        {"column": "gender", "type": "enum"},
        {"column": "email", "type": "varchar"},
        {"column": "phone", "type": "varchar"},
        {"column": "city", "type": "varchar"},
        {"column": "state", "type": "varchar"},
        {"column": "country", "type": "varchar"},
        {"column": "registration_date", "type": "date"},
        {"column": "region_id", "type": "int"}
    ],
    "employees": [
        {"column": "employee_id", "type": "int"},
        {"column": "first_name", "type": "varchar"},
        {"column": "last_name", "type": "varchar"},
        {"column": "email", "type": "varchar"},
        {"column": "phone", "type": "varchar"},
        {"column": "department", "type": "varchar"},
        {"column": "hire_date", "type": "date"},
        {"column": "salary", "type": "decimal"}
    ],
    "orders": [
        {"column": "order_id", "type": "int"},
        {"column": "customer_id", "type": "int"},
        {"column": "order_date", "type": "date"},
        {"column": "order_status", "type": "varchar"},
        {"column": "total_amount", "type": "decimal"},
        {"column": "shipper_id", "type": "int"}
    ],
    "order_items": [
        {"column": "order_item_id", "type": "int"},
        {"column": "order_id", "type": "int"},
        {"column": "product_id", "type": "int"},
        {"column": "quantity", "type": "int"},
        {"column": "unit_price", "type": "decimal"}
    ],
    "payments": [
        {"column": "payment_id", "type": "int"},
        {"column": "order_id", "type": "int"},
        {"column": "payment_date", "type": "date"},
        {"column": "payment_method", "type": "varchar"},
        {"column": "payment_status", "type": "varchar"},
        {"column": "amount", "type": "decimal"}
    ],
    "products": [
        {"column": "product_id", "type": "int"},
        {"column": "product_name", "type": "varchar"},
        {"column": "category_id", "type": "int"},
        {"column": "supplier_id", "type": "int"},
        {"column": "unit_price", "type": "decimal"},
        {"column": "stock_quantity", "type": "int"},
        {"column": "created_at", "type": "date"}
    ],
    "regions": [
        {"column": "region_id", "type": "int"},
        {"column": "region_name", "type": "varchar"},
        {"column": "manager_name", "type": "varchar"}
    ],
    "shippers": [
        {"column": "shipper_id", "type": "int"},
        {"column": "shipper_name", "type": "varchar"},
        {"column": "phone", "type": "varchar"}
    ],
    "suppliers": [
        {"column": "supplier_id", "type": "int"},
        {"column": "supplier_name", "type": "varchar"},
        {"column": "contact_name", "type": "varchar"},
        {"column": "email", "type": "varchar"},
        {"column": "phone", "type": "varchar"},
        {"column": "city", "type": "varchar"},
        {"column": "country", "type": "varchar"}
    ]
}


def get_database_schema(session_id: str = None):
    """
    Dynamically loads schema based on live session active dataset mode (CSV or MySQL).
    """
    active_mode = "mysql"
    active_table = "uploaded_data"
    csv_db_path = "uploaded_dataset.db"

    try:
        import app.main as main_module
        if session_id:
            active_mode = main_module.get_session_active_mode(session_id)
            active_table = main_module.get_session_active_table(session_id)
            csv_db_path = main_module.get_session_db_path(session_id)
        else:
            active_mode = "mysql"
    except Exception:
        active_mode = "mysql"

    if active_mode == "csv" and os.path.exists(csv_db_path):
        try:
            conn = sqlite3.connect(csv_db_path)
            cursor = conn.cursor()
            
            cursor.execute(f"PRAGMA table_info(`{active_table}`);")
            cols = cursor.fetchall()
            
            if not cols:
                cursor.execute(f"PRAGMA table_info(`uploaded_data`);")
                cols = cursor.fetchall()
                active_table = "uploaded_data"

            schema = {}
            if cols:
                schema["uploaded_data"] = [{"column": col[1], "type": col[2]} for col in cols]
                schema[active_table] = [{"column": col[1], "type": col[2]} for col in cols]
            
            conn.close()
            if schema:
                return schema
        except Exception as e:
            print("Error reading SQLite CSV schema:", e)

    # Load MySQL database schema
    try:
        connection = get_connection()
        cursor = connection.cursor()

        query = """
        SELECT
            TABLE_NAME,
            COLUMN_NAME,
            DATA_TYPE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'business_db'
        ORDER BY TABLE_NAME, ORDINAL_POSITION;
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        schema = {}
        for table_name, column_name, data_type in rows:
            if table_name not in schema:
                schema[table_name] = []

            schema[table_name].append({
                "column": column_name,
                "type": data_type
            })

        if schema:
            return schema
        return MYSQL_SCHEMA_FALLBACK
    except Exception as err:
        print("MySQL Schema Loader Warning, using schema fallback:", err)
        return MYSQL_SCHEMA_FALLBACK