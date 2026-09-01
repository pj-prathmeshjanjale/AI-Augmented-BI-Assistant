"""
Knowledge Documents and Semantic Knowledge Base for Text-to-SQL RAG Pipeline.
Contains detailed business definitions, schema semantics, join rules, KPIs, and validated SQL patterns.
"""

from typing import List
from langchain_core.documents import Document


def get_knowledge_documents() -> List[Document]:
    """
    Returns a curated list of LangChain Document objects with rich metadata
    representing the enterprise business intelligence domain knowledge.
    """
    raw_docs = [
        # =========================================================================
        # 1. TABLE SCHEMAS & COLUMN SEMANTICS
        # =========================================================================
        {
            "content": (
                "TABLE: orders\n"
                "DESCRIPTION: Stores high-level customer transactions and order headers.\n"
                "COLUMNS:\n"
                "- order_id (int, Primary Key): Unique transaction identifier.\n"
                "- customer_id (int, Foreign Key -> customers.customer_id): Identifier of purchasing customer.\n"
                "- order_date (date): Date when order was placed (YYYY-MM-DD).\n"
                "- order_status (varchar): Current order status ('Delivered', 'Shipped', 'Pending', 'Cancelled').\n"
                "- total_amount (decimal): Aggregate order value including all line items.\n"
                "- shipper_id (int, Foreign Key -> shippers.shipper_id): Carrier handling delivery."
            ),
            "metadata": {
                "doc_id": "schema_orders",
                "doc_type": "table_schema",
                "table": "orders",
                "topic": "orders_transactions",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: order_items\n"
                "DESCRIPTION: Granular line-item breakdown of individual products purchased in an order.\n"
                "COLUMNS:\n"
                "- order_item_id (int, Primary Key): Unique line-item ID.\n"
                "- order_id (int, Foreign Key -> orders.order_id): Parent order transaction ID.\n"
                "- product_id (int, Foreign Key -> products.product_id): Purchased item identifier.\n"
                "- quantity (int): Number of units purchased in this line item.\n"
                "- unit_price (decimal): Selling price per unit at transaction time."
            ),
            "metadata": {
                "doc_id": "schema_order_items",
                "doc_type": "table_schema",
                "table": "order_items",
                "topic": "line_items_revenue",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: customers\n"
                "DESCRIPTION: Customer demographic and profile directory.\n"
                "COLUMNS:\n"
                "- customer_id (int, Primary Key): Unique customer identifier.\n"
                "- first_name (varchar), last_name (varchar): Customer full name.\n"
                "- gender (enum: 'Male', 'Female', 'Other'): Customer gender.\n"
                "- email (varchar), phone (varchar): Contact credentials.\n"
                "- city (varchar), state (varchar), country (varchar): Geographic location.\n"
                "- registration_date (date): Account onboarding timestamp.\n"
                "- region_id (int, Foreign Key -> regions.region_id): Associated commercial region."
            ),
            "metadata": {
                "doc_id": "schema_customers",
                "doc_type": "table_schema",
                "table": "customers",
                "topic": "customer_demographics",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: products\n"
                "DESCRIPTION: Master catalog of available retail goods, catalog pricing, and inventory.\n"
                "COLUMNS:\n"
                "- product_id (int, Primary Key): Unique product identifier.\n"
                "- product_name (varchar): Commercial brand name of item.\n"
                "- category_id (int, Foreign Key -> categories.category_id): Parent merchandise classification.\n"
                "- supplier_id (int, Foreign Key -> suppliers.supplier_id): Sourcing partner vendor ID.\n"
                "- unit_price (decimal): Base MSRP catalog price.\n"
                "- stock_quantity (int): Available warehouse stock on hand.\n"
                "- created_at (date): Catalog listing date."
            ),
            "metadata": {
                "doc_id": "schema_products",
                "doc_type": "table_schema",
                "table": "products",
                "topic": "product_catalog",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: categories\n"
                "DESCRIPTION: High-level classification taxonomy for retail products.\n"
                "COLUMNS:\n"
                "- category_id (int, Primary Key): Unique category identifier.\n"
                "- category_name (varchar): Category label ('Electronics', 'Apparel', 'Home Goods', etc.).\n"
                "- description (text): Overview of product types within category."
            ),
            "metadata": {
                "doc_id": "schema_categories",
                "doc_type": "table_schema",
                "table": "categories",
                "topic": "merchandise_taxonomy",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: payments\n"
                "DESCRIPTION: Financial settlement logs and payment status tracking for customer orders.\n"
                "COLUMNS:\n"
                "- payment_id (int, Primary Key): Unique transaction payment record.\n"
                "- order_id (int, Foreign Key -> orders.order_id): Associated order identifier.\n"
                "- payment_date (date): Date payment was processed.\n"
                "- payment_method (varchar): Mode of payment ('Credit Card', 'Debit Card', 'UPI', 'PayPal', 'Net Banking', 'Cash').\n"
                "- payment_status (varchar): Settlement status ('Completed', 'Pending', 'Failed', 'Refunded').\n"
                "- amount (decimal): Paid currency amount."
            ),
            "metadata": {
                "doc_id": "schema_payments",
                "doc_type": "table_schema",
                "table": "payments",
                "topic": "payment_transactions",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: employees\n"
                "DESCRIPTION: Internal organizational personnel and compensation records.\n"
                "COLUMNS:\n"
                "- employee_id (int, Primary Key): Unique staff employee ID.\n"
                "- first_name (varchar), last_name (varchar): Staff full name.\n"
                "- email (varchar), phone (varchar): Corporate contact.\n"
                "- department (varchar): Functional business unit ('Sales', 'Marketing', 'Engineering', 'Operations', 'Finance').\n"
                "- hire_date (date): Employment start date.\n"
                "- salary (decimal): Annual or monthly base compensation."
            ),
            "metadata": {
                "doc_id": "schema_employees",
                "doc_type": "table_schema",
                "table": "employees",
                "topic": "workforce_payroll",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: regions\n"
                "DESCRIPTION: Commercial sales territories and regional governance hierarchy.\n"
                "COLUMNS:\n"
                "- region_id (int, Primary Key): Unique territory identifier.\n"
                "- region_name (varchar): Geographic sales territory name ('North America', 'Europe', 'Asia Pacific', 'Latin America', etc.).\n"
                "- manager_name (varchar): Executive regional director."
            ),
            "metadata": {
                "doc_id": "schema_regions",
                "doc_type": "table_schema",
                "table": "regions",
                "topic": "geography_territories",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: suppliers\n"
                "DESCRIPTION: External vendors and manufacturing partners supplying product inventory.\n"
                "COLUMNS:\n"
                "- supplier_id (int, Primary Key): Unique vendor identifier.\n"
                "- supplier_name (varchar): Vendor commercial business name.\n"
                "- contact_name (varchar), email (varchar), phone (varchar): Vendor account rep.\n"
                "- city (varchar), country (varchar): Supplier operational headquarters."
            ),
            "metadata": {
                "doc_id": "schema_suppliers",
                "doc_type": "table_schema",
                "table": "suppliers",
                "topic": "supply_chain_vendors",
                "source": "data_dictionary"
            }
        },
        {
            "content": (
                "TABLE: shippers\n"
                "DESCRIPTION: Logistics carriers and parcel freight providers for order fulfillment.\n"
                "COLUMNS:\n"
                "- shipper_id (int, Primary Key): Unique logistics carrier ID.\n"
                "- shipper_name (varchar): Delivery carrier brand name ('FedEx', 'UPS', 'DHL', etc.).\n"
                "- phone (varchar): Carrier customer dispatch line."
            ),
            "metadata": {
                "doc_id": "schema_shippers",
                "doc_type": "table_schema",
                "table": "shippers",
                "topic": "logistics_delivery",
                "source": "data_dictionary"
            }
        },

        # =========================================================================
        # 2. RELATIONAL JOIN PATHS & CONSTRAINTS
        # =========================================================================
        {
            "content": (
                "RELATIONSHIP & JOIN RULES:\n"
                "1. Orders to Customers: orders.customer_id = customers.customer_id\n"
                "2. Orders to Order Items: orders.order_id = order_items.order_id\n"
                "3. Order Items to Products: order_items.product_id = products.product_id\n"
                "4. Products to Categories: products.category_id = categories.category_id\n"
                "5. Products to Suppliers: products.supplier_id = suppliers.supplier_id\n"
                "6. Customers to Regions: customers.region_id = regions.region_id\n"
                "7. Orders to Payments: orders.order_id = payments.order_id\n"
                "8. Orders to Shippers: orders.shipper_id = shippers.shipper_id"
            ),
            "metadata": {
                "doc_id": "join_rules_master",
                "doc_type": "relationship",
                "table": "all",
                "topic": "table_relationships",
                "source": "schema_architecture"
            }
        },
        {
            "content": (
                "CATEGORY REVENUE JOIN PATH:\n"
                "To aggregate sales or revenue by product category:\n"
                "FROM categories c\n"
                "JOIN products p ON c.category_id = p.category_id\n"
                "JOIN order_items oi ON p.product_id = oi.product_id\n"
                "Calculation: SUM(oi.quantity * oi.unit_price) AS total_revenue\n"
                "GROUP BY c.category_name ORDER BY total_revenue DESC"
            ),
            "metadata": {
                "doc_id": "join_category_revenue",
                "doc_type": "relationship",
                "table": "categories",
                "topic": "revenue_by_category",
                "source": "business_logic"
            }
        },
        {
            "content": (
                "REGIONAL REVENUE JOIN PATH:\n"
                "To aggregate sales or customer volume by geographic territory:\n"
                "FROM regions r\n"
                "JOIN customers c ON r.region_id = c.region_id\n"
                "JOIN orders o ON c.customer_id = o.customer_id\n"
                "JOIN order_items oi ON o.order_id = oi.order_id\n"
                "Calculation: SUM(oi.quantity * oi.unit_price) AS regional_revenue\n"
                "GROUP BY r.region_name ORDER BY regional_revenue DESC"
            ),
            "metadata": {
                "doc_id": "join_regional_revenue",
                "doc_type": "relationship",
                "table": "regions",
                "topic": "revenue_by_region",
                "source": "business_logic"
            }
        },
        {
            "content": (
                "CUSTOMER SPENDING JOIN PATH:\n"
                "To rank top spending customers or customer lifetime purchase value:\n"
                "FROM customers c\n"
                "JOIN orders o ON c.customer_id = o.customer_id\n"
                "JOIN order_items oi ON o.order_id = oi.order_id\n"
                "Calculation: SUM(oi.quantity * oi.unit_price) AS total_spent, COUNT(DISTINCT o.order_id) AS total_orders\n"
                "GROUP BY c.customer_id, c.first_name, c.last_name ORDER BY total_spent DESC"
            ),
            "metadata": {
                "doc_id": "join_customer_spending",
                "doc_type": "relationship",
                "table": "customers",
                "topic": "customer_spending",
                "source": "business_logic"
            }
        },

        # =========================================================================
        # 3. KPI DEFINITIONS & ANALYTICAL FORMULAS
        # =========================================================================
        {
            "content": (
                "KPI FORMULA: Total Revenue\n"
                "DEFINITION: Gross commercial sales revenue across transactions.\n"
                "PRIMARY FORMULA: SUM(order_items.quantity * order_items.unit_price) AS total_revenue\n"
                "ALTERNATIVE (ORDER HEADER): SUM(orders.total_amount) AS total_revenue\n"
                "USAGE: Always format with 2 decimals and round as currency."
            ),
            "metadata": {
                "doc_id": "kpi_total_revenue",
                "doc_type": "kpi_rule",
                "table": "order_items",
                "topic": "revenue",
                "source": "kpi_handbook"
            }
        },
        {
            "content": (
                "KPI FORMULA: Average Order Value (AOV)\n"
                "DEFINITION: Mean monetary expenditure per completed transaction.\n"
                "FORMULA: AVG(orders.total_amount) AS average_order_value\n"
                "ALTERNATIVE VIA LINE ITEMS: SUM(order_items.quantity * order_items.unit_price) / COUNT(DISTINCT orders.order_id)\n"
                "USAGE: Group by time period, customer tier, or region to analyze basket sizing."
            ),
            "metadata": {
                "doc_id": "kpi_aov",
                "doc_type": "kpi_rule",
                "table": "orders",
                "topic": "average_order_value",
                "source": "kpi_handbook"
            }
        },
        {
            "content": (
                "KPI FORMULA: Monthly Sales Trend & Time Series\n"
                "DEFINITION: Revenue and order velocity aggregated by calendar month.\n"
                "MYSQL SYNTAX: DATE_FORMAT(orders.order_date, '%Y-%m') AS order_month\n"
                "SQLITE SYNTAX: strftime('%Y-%m', orders.order_date) AS order_month\n"
                "METRICS: SUM(orders.total_amount) AS monthly_revenue, COUNT(orders.order_id) AS order_count\n"
                "GROUP BY: order_month ORDER BY order_month ASC"
            ),
            "metadata": {
                "doc_id": "kpi_monthly_sales",
                "doc_type": "kpi_rule",
                "table": "orders",
                "topic": "time_series_sales",
                "source": "kpi_handbook"
            }
        },
        {
            "content": (
                "KPI FORMULA: Payment Method Distribution & Mix\n"
                "DEFINITION: Share of transactions and settlement volume across payment gateways.\n"
                "METRICS: payment_method, COUNT(payment_id) AS payment_count, SUM(amount) AS total_amount, "
                "ROUND(100.0 * COUNT(payment_id) / (SELECT COUNT(*) FROM payments), 2) AS percentage_share\n"
                "GROUP BY: payments.payment_method ORDER BY total_amount DESC"
            ),
            "metadata": {
                "doc_id": "kpi_payment_mix",
                "doc_type": "kpi_rule",
                "table": "payments",
                "topic": "payment_distribution",
                "source": "kpi_handbook"
            }
        },
        {
            "content": (
                "KPI FORMULA: Supplier Product Contribution & Inventory Value\n"
                "DEFINITION: Volume of merchandise catalog items and total inventory asset value provided per vendor.\n"
                "METRICS: suppliers.supplier_name, COUNT(products.product_id) AS product_count, "
                "SUM(products.stock_quantity * products.unit_price) AS total_inventory_value\n"
                "JOIN: suppliers s JOIN products p ON s.supplier_id = p.supplier_id\n"
                "GROUP BY: s.supplier_name ORDER BY product_count DESC"
            ),
            "metadata": {
                "doc_id": "kpi_supplier_contribution",
                "doc_type": "kpi_rule",
                "table": "suppliers",
                "topic": "supplier_performance",
                "source": "kpi_handbook"
            }
        },

        # =========================================================================
        # 4. BUSINESS TERMINOLOGY & SYNONYMS
        # =========================================================================
        {
            "content": (
                "BUSINESS TERMINOLOGY & MAPPINGS:\n"
                "- 'Best-selling product' / 'most popular product' / 'top product' -> ORDER BY SUM(order_items.quantity) DESC or SUM(order_items.quantity * order_items.unit_price) DESC LIMIT 5\n"
                "- 'High-value customer' / 'top customer' / 'VIP customer' -> ORDER BY SUM(orders.total_amount) DESC LIMIT 5\n"
                "- 'Sales performance by territory' -> Aggregate revenue grouped by regions.region_name\n"
                "- 'Delivery speed' / 'logistics partner' -> Aggregate order count grouped by shippers.shipper_name\n"
                "- 'Low stock' / 'inventory shortage' -> products WHERE stock_quantity < 20 ORDER BY stock_quantity ASC"
            ),
            "metadata": {
                "doc_id": "terminology_mappings",
                "doc_type": "business_term",
                "table": "all",
                "topic": "synonyms_glossary",
                "source": "analytics_standards"
            }
        },

        # =========================================================================
        # 5. VALIDATED SQL QUERY TEMPLATES & PATTERNS
        # =========================================================================
        {
            "content": (
                "SQL TEMPLATE: Top 5 products by revenue\n"
                "QUESTION: 'Which products generate the highest revenue?' / 'top 5 most sale product'\n"
                "SQL QUERY:\n"
                "SELECT p.product_name, SUM(oi.quantity * oi.unit_price) AS total_revenue\n"
                "FROM products p\n"
                "JOIN order_items oi ON p.product_id = oi.product_id\n"
                "GROUP BY p.product_id, p.product_name\n"
                "ORDER BY total_revenue DESC\n"
                "LIMIT 5;"
            ),
            "metadata": {
                "doc_id": "sql_template_top_products",
                "doc_type": "sql_example",
                "table": "products",
                "topic": "product_rankings",
                "source": "sql_benchmarks"
            }
        },
        {
            "content": (
                "SQL TEMPLATE: Region wise revenue breakdown\n"
                "QUESTION: 'Which region generated the highest revenue?' / 'region wise revenue'\n"
                "SQL QUERY:\n"
                "SELECT r.region_name, SUM(oi.quantity * oi.unit_price) AS total_revenue\n"
                "FROM regions r\n"
                "JOIN customers c ON r.region_id = c.region_id\n"
                "JOIN orders o ON c.customer_id = o.customer_id\n"
                "JOIN order_items oi ON o.order_id = oi.order_id\n"
                "GROUP BY r.region_id, r.region_name\n"
                "ORDER BY total_revenue DESC;"
            ),
            "metadata": {
                "doc_id": "sql_template_regional_revenue",
                "doc_type": "sql_example",
                "table": "regions",
                "topic": "regional_revenue",
                "source": "sql_benchmarks"
            }
        },
        {
            "content": (
                "SQL TEMPLATE: Monthly sales trend\n"
                "QUESTION: 'What is the monthly sales trend?' / 'monthly revenue'\n"
                "SQL QUERY (MySQL/SQLite):\n"
                "SELECT DATE_FORMAT(order_date, '%Y-%m') AS order_month, SUM(total_amount) AS total_revenue, COUNT(order_id) AS total_orders\n"
                "FROM orders\n"
                "GROUP BY DATE_FORMAT(order_date, '%Y-%m')\n"
                "ORDER BY order_month ASC;"
            ),
            "metadata": {
                "doc_id": "sql_template_monthly_sales",
                "doc_type": "sql_example",
                "table": "orders",
                "topic": "sales_trends",
                "source": "sql_benchmarks"
            }
        },
        {
            "content": (
                "SQL TEMPLATE: Previous month sales & calculations\n"
                "QUESTION: 'what is the calculations of previous month' / 'last month sales' / 'previous month revenue'\n"
                "SQL QUERY:\n"
                "SELECT \n"
                "    DATE_FORMAT(o.order_date, '%Y-%m') AS order_month,\n"
                "    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,\n"
                "    COUNT(DISTINCT o.order_id) AS total_orders,\n"
                "    COUNT(DISTINCT o.customer_id) AS active_customers,\n"
                "    ROUND(SUM(oi.quantity * oi.unit_price) / COUNT(DISTINCT o.order_id), 2) AS average_order_value\n"
                "FROM orders o\n"
                "JOIN order_items oi ON o.order_id = oi.order_id\n"
                "WHERE DATE_FORMAT(o.order_date, '%Y-%m') = DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m')\n"
                "GROUP BY DATE_FORMAT(o.order_date, '%Y-%m');"
            ),
            "metadata": {
                "doc_id": "sql_template_previous_month",
                "doc_type": "sql_example",
                "table": "orders",
                "topic": "time_based_analytics",
                "source": "sql_benchmarks"
            }
        },
        {
            "content": (
                "DATE & TIME FILTERING BEST PRACTICES:\n"
                "- Previous month: DATE_FORMAT(order_date, '%Y-%m') = DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m')\n"
                "- Current month: DATE_FORMAT(order_date, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')\n"
                "- Last 30 days: order_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)\n"
                "- Specific year: YEAR(order_date) = 2024 or strftime('%Y', order_date) = '2024'\n"
                "- Note: CURDATE() automatically references the current active transaction date."
            ),
            "metadata": {
                "doc_id": "kpi_time_series_filtering",
                "doc_type": "business_rule",
                "table": "orders",
                "topic": "date_time_rules",
                "source": "analytics_standards"
            }
        }
    ]

    return [Document(page_content=item["content"], metadata=item["metadata"]) for item in raw_docs]
