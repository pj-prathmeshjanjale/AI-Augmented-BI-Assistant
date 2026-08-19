# Business Database Schema Context

Database: business_db

## 1. categories

Purpose:
Stores product categories.

Columns:
- category_id: Primary key
- category_name: Unique category name
- description: Category description

---

## 2. customers

Purpose:
Stores customer information.

Columns:
- customer_id: Primary key
- first_name: Customer first name
- last_name: Customer last name
- gender: Customer gender
- email: Customer email
- phone: Customer phone
- city: Customer city
- state: Customer state
- country: Customer country
- registration_date: Customer registration date
- region_id: References regions.region_id

Relationship:
customers.region_id → regions.region_id

---

## 3. employees

Purpose:
Stores employee information.

Columns:
- employee_id: Primary key
- first_name: Employee first name
- last_name: Employee last name
- email: Employee email
- phone: Employee phone
- department: Employee department
- hire_date: Employee hiring date
- salary: Employee salary

Note:
Employees are currently independent from the sales transaction tables.

---

## 4. orders

Purpose:
Stores customer orders.

Columns:
- order_id: Primary key
- customer_id: References customers.customer_id
- order_date: Order date
- order_status: Order status
- total_amount: Total order amount
- shipper_id: References shippers.shipper_id

Relationships:
orders.customer_id → customers.customer_id
orders.shipper_id → shippers.shipper_id

---

## 5. order_items

Purpose:
Stores individual products contained in each order.

Columns:
- order_item_id: Primary key
- order_id: References orders.order_id
- product_id: References products.product_id
- quantity: Quantity purchased
- unit_price: Price per unit

Relationships:
order_items.order_id → orders.order_id
order_items.product_id → products.product_id

Revenue calculation:

quantity * unit_price

---

## 6. payments

Purpose:
Stores payment information for orders.

Columns:
- payment_id: Primary key
- order_id: References orders.order_id
- payment_date: Payment date
- payment_method: Payment method
- payment_status: Payment status
- amount: Payment amount

Relationship:
payments.order_id → orders.order_id

---

## 7. products

Purpose:
Stores products available for sale.

Columns:
- product_id: Primary key
- product_name: Product name
- category_id: References categories.category_id
- supplier_id: References suppliers.supplier_id
- unit_price: Product selling price
- stock_quantity: Current stock quantity
- created_at: Product creation date

Relationships:
products.category_id → categories.category_id
products.supplier_id → suppliers.supplier_id

---

## 8. regions

Purpose:
Stores geographical regions.

Columns:
- region_id: Primary key
- region_name: Unique region name
- manager_name: Region manager

Relationship:
regions.region_id ← customers.region_id

---

## 9. shippers

Purpose:
Stores shipping providers.

Columns:
- shipper_id: Primary key
- shipper_name: Shipper name
- phone: Shipper phone

Relationship:
shippers.shipper_id ← orders.shipper_id

---

## 10. suppliers

Purpose:
Stores product suppliers.

Columns:
- supplier_id: Primary key
- supplier_name: Supplier name
- contact_name: Supplier contact
- email: Supplier email
- phone: Supplier phone
- city: Supplier city
- country: Supplier country

Relationship:
suppliers.supplier_id ← products.supplier_id


# Important Business Metrics

## Revenue

Revenue is calculated from order items:

quantity * unit_price

Example:

quantity = 5
unit_price = 1000

Revenue = 5 * 1000 = 5000


## Order Revenue

Total revenue can be calculated using:

SUM(quantity * unit_price)

from order_items.


# Important Join Paths

## Customer → Revenue

customers
→ orders
→ order_items

## Category → Revenue

categories
→ products
→ order_items

## Supplier → Revenue

suppliers
→ products
→ order_items

## Region → Revenue

regions
→ customers
→ orders
→ order_items

## Shipper → Orders

shippers
→ orders

## Order → Payment

orders
→ payments


# Example Business Question

Question:

"Which category generated the highest revenue?"

Required tables:

categories
→ products
→ order_items

Revenue:

SUM(order_items.quantity * order_items.unit_price)


# Example SQL

SELECT
    c.category_name,
    SUM(oi.quantity * oi.unit_price) AS revenue
FROM categories c
JOIN products p
    ON c.category_id = p.category_id
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY c.category_name
ORDER BY revenue DESC;