-- ====================================================================
-- PROJECT: NovaMart Retail Sales & Customer Analytics Portfolio Project
-- SCRIPT: 01_schema.sql
-- DESCRIPTION: Database DDL creating relational tables for NovaMart.
-- ====================================================================

-- 1. Enable Foreign Key Support (for SQLite)
PRAGMA foreign_keys = ON;

-- 2. Clean up existing tables if they exist (reverse order of dependencies)
DROP TABLE IF EXISTS order_items;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

-- --------------------------------------------------------------------
-- TABLE 1: customers
-- Purpose: Stores customer profile, geographic and segmentation attributes.
-- --------------------------------------------------------------------
CREATE TABLE customers (
    customer_id      INTEGER PRIMARY KEY,
    first_name       TEXT NOT NULL,
    last_name        TEXT NOT NULL,
    email            TEXT UNIQUE NOT NULL,
    customer_segment TEXT NOT NULL CHECK(customer_segment IN ('Consumer', 'Corporate', 'Small Business')),
    city             TEXT NOT NULL,
    state            TEXT NOT NULL,
    region           TEXT NOT NULL CHECK(region IN ('East', 'West', 'Midwest', 'South')),
    signup_date      TEXT NOT NULL  -- Format: YYYY-MM-DD
);

-- --------------------------------------------------------------------
-- TABLE 2: products
-- Purpose: Stores master catalog of items with pricing and cost structure.
-- --------------------------------------------------------------------
CREATE TABLE products (
    product_id       INTEGER PRIMARY KEY,
    product_name     TEXT NOT NULL,
    category         TEXT NOT NULL,
    sub_category     TEXT NOT NULL,
    unit_cost        REAL NOT NULL CHECK(unit_cost > 0),
    unit_price       REAL NOT NULL CHECK(unit_price >= unit_cost)
);

-- --------------------------------------------------------------------
-- TABLE 3: orders
-- Purpose: Stores transaction headers, customer links, dates, and status.
-- --------------------------------------------------------------------
CREATE TABLE orders (
    order_id         INTEGER PRIMARY KEY,
    customer_id      INTEGER NOT NULL,
    order_date       TEXT NOT NULL, -- Format: YYYY-MM-DD
    shipping_mode    TEXT NOT NULL CHECK(shipping_mode IN ('Standard', 'Express', 'Same Day')),
    payment_method   TEXT NOT NULL CHECK(payment_method IN ('Credit Card', 'Debit Card', 'PayPal', 'Gift Card')),
    order_status     TEXT NOT NULL CHECK(order_status IN ('Completed', 'Returned', 'Cancelled')),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

-- --------------------------------------------------------------------
-- TABLE 4: order_items
-- Purpose: Fact table recording individual line-item sales per order.
-- --------------------------------------------------------------------
CREATE TABLE order_items (
    order_item_id    INTEGER PRIMARY KEY,
    order_id         INTEGER NOT NULL,
    product_id       INTEGER NOT NULL,
    quantity         INTEGER NOT NULL CHECK(quantity > 0),
    discount         REAL NOT NULL DEFAULT 0.0 CHECK(discount >= 0.0 AND discount <= 0.30),
    line_total       REAL NOT NULL CHECK(line_total >= 0),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

-- --------------------------------------------------------------------
-- Helpful Indexes for Analytical Performance
-- --------------------------------------------------------------------
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_orders_order_date ON orders(order_date);
CREATE INDEX idx_order_items_order_id ON order_items(order_id);
CREATE INDEX idx_order_items_product_id ON order_items(product_id);
