import sys
import os
import sqlite3
import mysql.connector

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from app.database.connection import get_connection

DEFAULT_DB_PATH = "default_business.db"


def export_mysql_to_sqlite():
    """
    Exports all tables and records from local MySQL 'business_db' 
    into 'default_business.db' so the cloud web demo has 100% of your real dataset!
    """
    print("Connecting to your local MySQL database 'business_db'...")
    try:
        mysql_conn = get_connection()
        mysql_cursor = mysql_conn.cursor()
    except Exception as e:
        print(f"Could not connect to local MySQL: {e}")
        print("Ensure MySQL is running on localhost:3306 and credentials in connection.py or .env match.")
        return False

    # Get list of all tables in business_db
    mysql_cursor.execute("SHOW TABLES;")
    tables = [t[0] for t in mysql_cursor.fetchall()]
    print(f"Found {len(tables)} tables in local MySQL: {', '.join(tables)}")

    sqlite_conn = sqlite3.connect(DEFAULT_DB_PATH)
    sqlite_cursor = sqlite_conn.cursor()

    for table in tables:
        # Fetch columns and data types
        mysql_cursor.execute(f"DESCRIBE `{table}`;")
        cols_info = mysql_cursor.fetchall()
        
        col_names = []
        col_defs = []
        for col in cols_info:
            c_name = col[0]
            c_type = str(col[1]).lower()
            
            # Map MySQL types to SQLite types
            if "int" in c_type:
                sq_type = "INTEGER"
            elif "decimal" in c_type or "float" in c_type or "double" in c_type:
                sq_type = "REAL"
            else:
                sq_type = "TEXT"
                
            col_names.append(c_name)
            col_defs.append(f"`{c_name}` {sq_type}")

        # Drop and create table in SQLite
        sqlite_cursor.execute(f"DROP TABLE IF EXISTS `{table}`;")
        create_sql = f"CREATE TABLE `{table}` ({', '.join(col_defs)});"
        sqlite_cursor.execute(create_sql)

        # Fetch all rows from MySQL
        mysql_cursor.execute(f"SELECT * FROM `{table}`;")
        rows = mysql_cursor.fetchall()

        # Convert row values preserving numeric types
        clean_rows = []
        for r in rows:
            clean_r = []
            for col_idx, item in enumerate(r):
                if item is None:
                    clean_r.append(None)
                else:
                    c_type = str(cols_info[col_idx][1]).lower()
                    if "int" in c_type:
                        try:
                            clean_r.append(int(item))
                        except Exception:
                            clean_r.append(str(item))
                    elif "decimal" in c_type or "float" in c_type or "double" in c_type:
                        try:
                            clean_r.append(float(item))
                        except Exception:
                            clean_r.append(str(item))
                    else:
                        clean_r.append(str(item))
            clean_rows.append(clean_r)

        if clean_rows:
            placeholders = ", ".join(["?"] * len(col_names))
            insert_sql = f"INSERT INTO `{table}` VALUES ({placeholders})"
            sqlite_cursor.executemany(insert_sql, clean_rows)

        print(f"  Exported table '{table}': {len(clean_rows):,} rows transferred.")

    sqlite_conn.commit()
    sqlite_conn.close()
    mysql_cursor.close()
    mysql_conn.close()

    print(f"\nSuccessfully exported 100% of your real MySQL data to '{DEFAULT_DB_PATH}'!")
    return True


if __name__ == "__main__":
    export_mysql_to_sqlite()
