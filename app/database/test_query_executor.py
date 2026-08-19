from app.database.query_executor import execute_query


sql = """
SELECT
    c.category_name,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM categories c
JOIN products p
    ON c.category_id = p.category_id
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY c.category_name
ORDER BY revenue DESC
LIMIT 5;
"""


results = execute_query(sql)


print("\nQuery Results:\n")

for row in results:
    print(row)