from app.database.connection import get_connection


def get_database_schema():
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