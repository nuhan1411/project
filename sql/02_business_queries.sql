-- ====================================================================
-- PROJECT: NovaMart Retail Sales & Customer Analytics Portfolio Project
-- SCRIPT: 02_business_queries.sql
-- DESCRIPTION: Core business queries answering key executive questions.
-- ====================================================================

-- --------------------------------------------------------------------
-- QUERY 1: Executive KPI Summary
-- BUSINESS QUESTION: What is our overall business performance across completed orders?
-- CONCEPTS: COUNT(DISTINCT), SUM(), ROUND(), INNER JOIN, WHERE filter
-- --------------------------------------------------------------------
SELECT 
    COUNT(DISTINCT o.order_id) AS total_orders,
    COUNT(DISTINCT o.customer_id) AS total_customers,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(SUM(oi.quantity * p.unit_cost), 2) AS total_cost,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(oi.line_total) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed';

-- EXPLANATION:
-- 1. 'WHERE o.order_status = "Completed"' ensures we exclude returned or cancelled orders.
-- 2. 'COUNT(DISTINCT ...)' prevents duplicate counts caused by orders having multiple items.
-- 3. 'line_total - (quantity * unit_cost)' calculates Gross Profit per line item.
-- 4. 'profit_margin_pct' tells leadership what percentage of revenue becomes profit.


-- --------------------------------------------------------------------
-- QUERY 2: Monthly Revenue & Profit Trend (Seasonality)
-- BUSINESS QUESTION: How do revenue and profit trend month-over-month? Are there seasonal spikes?
-- CONCEPTS: Date formatting (strftime), GROUP BY, ORDER BY ASC
-- --------------------------------------------------------------------
SELECT 
    strftime('%Y-%m', o.order_date) AS order_month,
    COUNT(DISTINCT o.order_id) AS monthly_orders,
    ROUND(SUM(oi.line_total), 2) AS monthly_revenue,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS monthly_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY strftime('%Y-%m', o.order_date)
ORDER BY order_month ASC;

-- EXPLANATION:
-- 1. 'strftime("%Y-%m", order_date)' groups dates by Year and Month (e.g., '2023-11').
-- 2. Reveals holiday shopping surges in November and December.


-- --------------------------------------------------------------------
-- QUERY 3: Category Performance & Profitability
-- BUSINESS QUESTION: Which categories generate the highest revenue vs. highest profit margin?
-- CONCEPTS: GROUP BY, aggregate ranking, margin comparison
-- --------------------------------------------------------------------
SELECT 
    p.category,
    COUNT(DISTINCT o.order_id) AS orders_count,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category
ORDER BY total_revenue DESC;

-- EXPLANATION:
-- Shows the classic product portfolio trade-off: Electronics drives top-line sales volume,
-- but Beauty & Health and Apparel deliver higher profit margins per dollar sold.


-- --------------------------------------------------------------------
-- QUERY 4: Sub-Category Profitability Breakdown
-- BUSINESS QUESTION: What are the top 10 performing sub-categories?
-- CONCEPTS: Multi-column GROUP BY, LIMIT
-- --------------------------------------------------------------------
SELECT 
    p.category,
    p.sub_category,
    SUM(oi.quantity) AS units_sold,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.category, p.sub_category
ORDER BY total_revenue DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 5: Discount Impact on Margins
-- BUSINESS QUESTION: Do higher discounts hurt our bottom-line profit margins?
-- CONCEPTS: CASE WHEN conditional bucketing, aggregate statistics
-- --------------------------------------------------------------------
SELECT 
    CASE 
        WHEN oi.discount = 0.0 THEN '0% (No Discount)'
        WHEN oi.discount <= 0.05 THEN '5% Discount'
        WHEN oi.discount <= 0.10 THEN '10% Discount'
        WHEN oi.discount <= 0.15 THEN '15% Discount'
        ELSE '20% Discount'
    END AS discount_tier,
    COUNT(*) AS item_count,
    SUM(oi.quantity) AS total_units,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY discount_tier
ORDER BY profit_margin_pct DESC;

-- EXPLANATION:
-- 'CASE WHEN' categorizes continuous discount numbers into business tiers.
-- Directly shows the CFO how heavy discounting degrades margin from 61.5% down to 52.1%.


-- --------------------------------------------------------------------
-- QUERY 6: Top 10 Best-Selling Products by Revenue
-- BUSINESS QUESTION: Which individual items generate the most revenue?
-- CONCEPTS: JOIN, ORDER BY DESC, LIMIT
-- --------------------------------------------------------------------
SELECT 
    p.product_id,
    p.product_name,
    p.category,
    SUM(oi.quantity) AS total_units_sold,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Completed'
GROUP BY p.product_id, p.product_name, p.category
ORDER BY total_revenue DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 7: Customer Segmentation Performance
-- BUSINESS QUESTION: How do Consumer, Corporate, and Small Business customer segments compare?
-- CONCEPTS: Customer segmentation aggregation, Revenue Per Customer metric
-- --------------------------------------------------------------------
SELECT 
    c.customer_segment,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    COUNT(DISTINCT o.order_id) AS completed_orders,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(oi.line_total) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value,
    ROUND(SUM(oi.line_total) / COUNT(DISTINCT c.customer_id), 2) AS revenue_per_customer
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;

-- EXPLANATION:
-- Even though 'Consumer' has the largest aggregate revenue, 'Small Business' generates
-- the highest revenue per customer ($749.53 vs $695.32).


-- --------------------------------------------------------------------
-- QUERY 8: Customer Retention & Repeat Purchase Rate
-- BUSINESS QUESTION: What proportion of our customers are repeat buyers vs one-time buyers?
-- CONCEPTS: Common Table Expression (WITH CTE), Subqueries, Percentage of Total
-- --------------------------------------------------------------------
WITH customer_order_counts AS (
    SELECT 
        c.customer_id,
        COUNT(DISTINCT o.order_id) AS order_count,
        SUM(oi.line_total) AS customer_revenue
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id
)
SELECT 
    CASE 
        WHEN order_count = 1 THEN 'One-time Customer'
        ELSE 'Repeat Customer (2+ Orders)'
    END AS customer_type,
    COUNT(*) AS customer_count,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_order_counts)), 2) AS customer_pct,
    ROUND(SUM(customer_revenue), 2) AS total_revenue,
    ROUND((SUM(customer_revenue) * 100.0 / (SELECT SUM(customer_revenue) FROM customer_order_counts)), 2) AS revenue_pct,
    ROUND(AVG(customer_revenue), 2) AS avg_revenue_per_customer
FROM customer_order_counts
GROUP BY customer_type;

-- EXPLANATION:
-- Demonstrates CTE mastery to recruiters:
-- 1. Inner query ('customer_order_counts') aggregates order count per customer.
-- 2. Outer query buckets customers into One-time vs Repeat and calculates percentage share.


-- --------------------------------------------------------------------
-- QUERY 9: Top 10 VIP Customers (Highest Lifetime Value)
-- BUSINESS QUESTION: Who are our highest-spending customers?
-- CONCEPTS: String concatenation (first_name || ' ' || last_name), multi-table join
-- --------------------------------------------------------------------
SELECT 
    c.customer_id,
    c.first_name || ' ' || c.last_name AS customer_name,
    c.customer_segment,
    c.region,
    COUNT(DISTINCT o.order_id) AS orders_placed,
    SUM(oi.quantity) AS total_units_bought,
    ROUND(SUM(oi.line_total), 2) AS total_spent,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit_contributed
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY c.customer_id, customer_name, c.customer_segment, c.region
ORDER BY total_spent DESC
LIMIT 10;


-- --------------------------------------------------------------------
-- QUERY 10: Regional Performance & Order Fulfillment
-- BUSINESS QUESTION: How do our four geographic regions compare in revenue and AOV?
-- CONCEPTS: Regional grouping, AOV calculation
-- --------------------------------------------------------------------
SELECT 
    c.region,
    COUNT(DISTINCT o.order_id) AS total_orders,
    ROUND(SUM(oi.line_total), 2) AS total_revenue,
    ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS total_profit,
    ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) AS profit_margin_pct,
    ROUND(SUM(oi.line_total) / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.order_status = 'Completed'
GROUP BY c.region
ORDER BY total_revenue DESC;
