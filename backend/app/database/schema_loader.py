import os
import sqlite3
from app.database.connection import get_connection


def get_database_schema():
    """
    Dynamically loads schema based on live active dataset mode (CSV or MySQL).
    """
    csv_db_path = "uploaded_dataset.db"
    
    active_mode = "mysql"
    active_table = "uploaded_data"
    try:
        import app.main as main_module
        active_mode = getattr(main_module, 'ACTIVE_DATASET_MODE', 'mysql')
        active_table = getattr(main_module, 'ACTIVE_CSV_TABLE', 'uploaded_data')
    except Exception:
        active_mode = "csv" if os.path.exists(csv_db_path) else "mysql"

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

        return schema
    except Exception as err:
        print("MySQL Schema Loader Warning:", err)
        return {}