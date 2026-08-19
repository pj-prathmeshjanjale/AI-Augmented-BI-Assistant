from app.database.connection import get_connection
from app.ai.sql_validator import validate_sql


def execute_query(sql):

    # Step 1: Validate SQL
    is_safe, message = validate_sql(sql)

    if not is_safe:
        raise ValueError(f"Unsafe SQL query: {message}")

    # Step 2: Connect to MySQL
    connection = get_connection()

    cursor = connection.cursor(dictionary=True)

    try:
        # Step 3: Execute query
        cursor.execute(sql)

        # Step 4: Fetch results
        results = cursor.fetchall()

        return results

    finally:
        cursor.close()
        connection.close()