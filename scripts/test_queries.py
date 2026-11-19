"""
Run and validate all 10 business SQL queries against novamart.db.
Prints exact results to ensure no hallucinated numbers.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(r"w:\projectsql\data\novamart.db")
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

queries = {
    "Query 1: Executive KPI Summary": """
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
    """,
    
    "Query 2: Monthly Revenue & Profit Trend": """
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
    """,
    
    "Query 3: Category Performance & Profitability": """
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
    """,
    
    "Query 4: Sub-Category Ranking": """
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
    """,
    
    "Query 5: Impact of Discounts on Profit Margins": """
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
    """,
    
    "Query 6: Top 10 Best-Selling Products by Revenue": """
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
    """,
    
    "Query 7: Customer Segmentation Performance": """
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
    """,
    
    "Query 8: Customer Repeat Purchase Rate": """
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
    """,
    
    "Query 9: Top 10 VIP Customers": """
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
    """,
    
    "Query 10: Regional Performance & Order Fulfillment": """
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
    """
}

for title, sql in queries.items():
    print(f"\n==========================================")
    print(f"{title}")
    print(f"==========================================")
    cursor.execute(sql)
    col_names = [description[0] for description in cursor.description]
    rows = cursor.fetchall()
    
    # Print header
    header = " | ".join(col_names)
    print(header)
    print("-" * len(header))
    for r in rows:
        print(" | ".join(str(val) for val in r))

conn.close()
