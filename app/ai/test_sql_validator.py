from app.ai.sql_validator import validate_sql


safe_sql = """
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
LIMIT 1;
"""


unsafe_sql = """
DELETE FROM customers;
"""


is_safe, message = validate_sql(safe_sql)

print("SAFE QUERY TEST")
print("Result:", is_safe)
print("Message:", message)


is_safe, message = validate_sql(unsafe_sql)

print("\nUNSAFE QUERY TEST")
print("Result:", is_safe)
print("Message:", message)