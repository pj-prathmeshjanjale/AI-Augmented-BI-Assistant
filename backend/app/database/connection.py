import os
import mysql.connector
from mysql.connector import Error

# =========================================================================
# DATABASE CONFIGURATION
# Set your MySQL credentials here or in a .env file!
# =========================================================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER", "root")          # Your MySQL username
DB_PASSWORD = os.getenv("DB_PASSWORD", "")       # Your MySQL password
DB_NAME = os.getenv("DB_NAME", "business_db")    # Change this to your Database Name!


def get_connection():
    """
    Establishes and returns a connection to your MySQL database.
    """
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL Database '{DB_NAME}': {e}")
        raise e

# Alias for backwards compatibility
get_db_connection = get_connection