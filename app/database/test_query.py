from connection import get_connection


connection = get_connection()
cursor = connection.cursor()

query = """
SELECT
    category_id,
    category_name
FROM categories
LIMIT 10;
"""

cursor.execute(query)

results = cursor.fetchall()

for row in results:
    print(row)

cursor.close()
connection.close()