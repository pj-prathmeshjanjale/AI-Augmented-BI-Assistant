from app.database.schema_loader import get_database_schema


BUSINESS_RULES = """
BUSINESS RULES:

1. Revenue
Revenue is calculated as:
quantity * unit_price

Revenue source:
order_items.quantity * order_items.unit_price

2. Category Revenue
To calculate revenue by category:
categories
→ products
→ order_items

Join conditions:
categories.category_id = products.category_id
products.product_id = order_items.product_id

3. Customer Revenue
To calculate revenue by customer:
customers
→ orders
→ order_items

Join conditions:
customers.customer_id = orders.customer_id
orders.order_id = order_items.order_id

4. Region Revenue
To calculate revenue by region:
regions
→ customers
→ orders
→ order_items

Join conditions:
regions.region_id = customers.region_id
customers.customer_id = orders.customer_id
orders.order_id = order_items.order_id

5. Supplier Revenue
To calculate revenue by supplier:
suppliers
→ products
→ order_items

Join conditions:
suppliers.supplier_id = products.supplier_id
products.product_id = order_items.product_id

6. Order Payments
Payments are connected to orders through:
payments.order_id = orders.order_id

7. Product Stock
Current product inventory is stored in:
products.stock_quantity

8. Order Total
Order-level total is stored in:
orders.total_amount
"""


def build_schema_context():

    schema = get_database_schema()

    context = "DATABASE: business_db\n\n"

    for table_name, columns in schema.items():

        context += f"TABLE: {table_name}\n"
        context += "COLUMNS:\n"

        for column in columns:
            context += f"- {column['column']} ({column['type']})\n"

        context += "\n"

    context += BUSINESS_RULES

    return context


