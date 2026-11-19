"""
Build professional Excel Portfolio Workbook: NovaMart_Sales_Analysis.xlsx
Includes:
- Executive Dashboard (KPI cards, 4 native interactive charts, key findings)
- Monthly & Category Analysis (Summary tables, Excel formulas)
- Customer & Regional Analysis (Segmentation, Repeat rates, Top 10 VIPs)
- Orders_Clean_Data (Full transaction table with native Excel formulas)
- Products_Catalog (Reference table)
- Customers_Master (Reference table)
"""

import sqlite3
import xlsxwriter
from pathlib import Path

DB_PATH = Path(r"w:\projectsql\data\novamart.db")
EXCEL_PATH = Path(r"w:\projectsql\excel\NovaMart_Sales_Analysis.xlsx")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Query all completed transaction rows joined
cursor.execute("""
    SELECT 
        o.order_id,
        o.order_date,
        strftime('%Y', o.order_date) AS order_year,
        strftime('%Y-%m', o.order_date) AS order_month,
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.customer_segment,
        c.region,
        c.state,
        p.product_id,
        p.product_name,
        p.category,
        p.sub_category,
        oi.quantity,
        p.unit_cost,
        p.unit_price,
        oi.discount,
        oi.line_total,
        ROUND(oi.quantity * p.unit_cost, 2) AS cogs,
        ROUND(oi.line_total - (oi.quantity * p.unit_cost), 2) AS gross_profit,
        ROUND((oi.line_total - (oi.quantity * p.unit_cost)) / oi.line_total, 4) AS margin_pct
    FROM orders o
    JOIN customers c ON o.customer_id = c.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed'
    ORDER BY o.order_date ASC, o.order_id ASC;
""")
clean_data_rows = cursor.fetchall()

# Query monthly summary
cursor.execute("""
    SELECT 
        strftime('%Y-%m', o.order_date) AS month_label,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(SUM(oi.line_total), 2) AS revenue,
        ROUND(SUM(oi.quantity * p.unit_cost), 2) AS cogs,
        ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS profit
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed'
    GROUP BY month_label
    ORDER BY month_label ASC;
""")
monthly_rows = cursor.fetchall()

# Query category summary
cursor.execute("""
    SELECT 
        p.category,
        COUNT(DISTINCT o.order_id) AS orders,
        SUM(oi.quantity) AS units,
        ROUND(SUM(oi.line_total), 2) AS revenue,
        ROUND(SUM(oi.quantity * p.unit_cost), 2) AS cogs,
        ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS profit
    FROM order_items oi
    JOIN products p ON oi.product_id = p.product_id
    JOIN orders o ON oi.order_id = o.order_id
    WHERE o.order_status = 'Completed'
    GROUP BY p.category
    ORDER BY revenue DESC;
""")
category_rows = cursor.fetchall()

# Query segment summary
cursor.execute("""
    SELECT 
        c.customer_segment,
        COUNT(DISTINCT c.customer_id) AS customers,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(SUM(oi.line_total), 2) AS revenue,
        ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS profit
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_segment
    ORDER BY revenue DESC;
""")
segment_rows = cursor.fetchall()

# Query regional summary
cursor.execute("""
    SELECT 
        c.region,
        COUNT(DISTINCT o.order_id) AS orders,
        ROUND(SUM(oi.line_total), 2) AS revenue,
        ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS profit
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.region
    ORDER BY revenue DESC;
""")
regional_rows = cursor.fetchall()

# Query Top 10 VIP customers
cursor.execute("""
    SELECT 
        c.customer_id,
        c.first_name || ' ' || c.last_name AS customer_name,
        c.customer_segment,
        c.region,
        COUNT(DISTINCT o.order_id) AS orders_placed,
        SUM(oi.quantity) AS total_units,
        ROUND(SUM(oi.line_total), 2) AS total_spent,
        ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) AS profit_contributed
    FROM customers c
    JOIN orders o ON c.customer_id = o.customer_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed'
    GROUP BY c.customer_id, customer_name, c.customer_segment, c.region
    ORDER BY total_spent DESC
    LIMIT 10;
""")
vip_rows = cursor.fetchall()

# Query products catalog
cursor.execute("SELECT product_id, product_name, category, sub_category, unit_cost, unit_price FROM products;")
catalog_rows = cursor.fetchall()

# Query customers master
cursor.execute("SELECT customer_id, first_name, last_name, email, customer_segment, city, state, region, signup_date FROM customers;")
customer_master_rows = cursor.fetchall()

conn.close()

# -------------------------------------------------------------
# BUILD WORKBOOK WITH XLSXWRITER
# -------------------------------------------------------------
workbook = xlsxwriter.Workbook(str(EXCEL_PATH))

# Palette: Executive Navy & Slate Blue
NAVY_HEADER = "#1B365D"
SLATE_BLUE = "#4A777A"
CARD_BG = "#F4F7FB"
BORDER_COLOR = "#D1D5DB"
LIGHT_ZEBRA = "#F9FAFB"
ACCENT_BLUE = "#2563EB"
ACCENT_GREEN = "#059669"

# Formats
fmt_title = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 18, 'bold': True, 'font_color': '#1E293B'
})
fmt_subtitle = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 10, 'font_color': '#64748B'
})

fmt_tbl_header = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 10, 'bold': True, 'bg_color': NAVY_HEADER,
    'font_color': '#FFFFFF', 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': NAVY_HEADER
})

fmt_tbl_header_left = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 10, 'bold': True, 'bg_color': NAVY_HEADER,
    'font_color': '#FFFFFF', 'align': 'left', 'valign': 'vcenter', 'border': 1, 'border_color': NAVY_HEADER
})

fmt_card_title = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'bold': True, 'font_color': '#64748B',
    'bg_color': CARD_BG, 'align': 'center', 'top': 1, 'left': 1, 'right': 1, 'border_color': BORDER_COLOR
})
fmt_card_value = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 16, 'bold': True, 'font_color': '#0F172A',
    'bg_color': CARD_BG, 'align': 'center', 'left': 1, 'right': 1, 'border_color': BORDER_COLOR
})
fmt_card_sub = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 8, 'font_color': '#10B981',
    'bg_color': CARD_BG, 'align': 'center', 'bottom': 1, 'left': 1, 'right': 1, 'border_color': BORDER_COLOR
})

fmt_cell_text = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'valign': 'vcenter', 'border': 1, 'border_color': BORDER_COLOR
})
fmt_cell_center = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'align': 'center', 'valign': 'vcenter', 'border': 1, 'border_color': BORDER_COLOR
})
fmt_cell_currency = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'num_format': '$#,##0.00', 'align': 'right', 'valign': 'vcenter', 'border': 1, 'border_color': BORDER_COLOR
})
fmt_cell_int = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'num_format': '#,##0', 'align': 'right', 'valign': 'vcenter', 'border': 1, 'border_color': BORDER_COLOR
})
fmt_cell_pct = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'num_format': '0.0%', 'align': 'right', 'valign': 'vcenter', 'border': 1, 'border_color': BORDER_COLOR
})

fmt_total_row_currency = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'bold': True, 'num_format': '$#,##0.00', 'bg_color': '#E2E8F0', 'top': 1, 'bottom': 2, 'border_color': '#475569'
})
fmt_total_row_int = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'bold': True, 'num_format': '#,##0', 'bg_color': '#E2E8F0', 'top': 1, 'bottom': 2, 'border_color': '#475569'
})
fmt_total_row_pct = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'bold': True, 'num_format': '0.0%', 'bg_color': '#E2E8F0', 'top': 1, 'bottom': 2, 'border_color': '#475569'
})
fmt_total_row_label = workbook.add_format({
    'font_name': 'Segoe UI', 'font_size': 9, 'bold': True, 'bg_color': '#E2E8F0', 'top': 1, 'bottom': 2, 'border_color': '#475569'
})

# =============================================================
# SHEET 1: Executive Dashboard
# =============================================================
ws_dash = workbook.add_worksheet("Executive Dashboard")
ws_dash.set_tab_color("#1E3A8A")
# Gridlines are enabled by default
ws_dash.hide_gridlines(0)

ws_dash.set_column('A:A', 3)
ws_dash.set_column('B:C', 16)
ws_dash.set_column('D:E', 16)
ws_dash.set_column('F:G', 16)
ws_dash.set_column('H:I', 16)
ws_dash.set_column('J:K', 16)
ws_dash.set_column('L:M', 16)

# Title Block
ws_dash.write('B2', "NovaMart Retail Performance Dashboard", fmt_title)
ws_dash.write('B3', "Executive KPI Overview, Customer Analytics & Category Profitability | Fiscal Years 2023 - 2024", fmt_subtitle)

# Top KPI Summary Cards (Row 5 - 7)
# Card 1: Total Revenue
ws_dash.merge_range('B5:C5', "TOTAL REVENUE", fmt_card_title)
ws_dash.merge_range('B6:C6', "=$G$22", fmt_card_value) # References category total
ws_dash.merge_range('B7:C7', "Completed Orders Only", fmt_card_sub)

# Card 2: Total Gross Profit
ws_dash.merge_range('D5:E5', "GROSS PROFIT", fmt_card_title)
ws_dash.merge_range('D6:E6', "=$I$22", fmt_card_value)
ws_dash.merge_range('D7:E7', "Revenue - COGS", fmt_card_sub)

# Card 3: Overall Profit Margin
ws_dash.merge_range('F5:G5', "PROFIT MARGIN %", fmt_card_title)
ws_dash.merge_range('F6:G6', "=$J$22", fmt_card_value)
ws_dash.merge_range('F7:G7', "Healthy Margins Across Categories", fmt_card_sub)

# Card 4: Completed Orders
ws_dash.merge_range('H5:I5', "COMPLETED ORDERS", fmt_card_title)
ws_dash.merge_range('H6:I6', "=$E$22", fmt_card_value)
ws_dash.merge_range('H7:I7', "91.0% Completion Rate", fmt_card_sub)

# Card 5: Active Customers
ws_dash.merge_range('J5:K5', "ACTIVE CUSTOMERS", fmt_card_title)
ws_dash.merge_range('J6:K6', 245, fmt_card_value)
ws_dash.merge_range('J7:K7', "86.9% Repeat Customer Rate", fmt_card_sub)

# Card 6: Average Order Value
ws_dash.merge_range('L5:M5', "AVG ORDER VALUE (AOV)", fmt_card_title)
ws_dash.merge_range('L6:M6', "=$G$22/$E$22", fmt_card_value)
ws_dash.merge_range('L7:M7', "Revenue per Order", fmt_card_sub)

# Dashboard Summary Data Tables (Used for driving Dashboard Charts)
ws_dash.write('B16', "Category Breakdown (Dashboard Summary)", workbook.add_format({'bold': True, 'font_size': 11}))
headers_dash_cat = ["Category", "Orders", "Units Sold", "Revenue", "COGS", "Gross Profit", "Margin %"]
dash_cat_cols = ['D', 'E', 'F', 'G', 'H', 'I', 'J']

for c_idx, h in enumerate(headers_dash_cat):
    ws_dash.write(16, c_idx + 3, h, fmt_tbl_header)

for r_idx, row in enumerate(category_rows, start=17):
    cat, orders_c, units, rev, cogs, profit = row
    ws_dash.write(r_idx, 3, cat, fmt_cell_text)
    ws_dash.write(r_idx, 4, orders_c, fmt_cell_int)
    ws_dash.write(r_idx, 5, units, fmt_cell_int)
    ws_dash.write(r_idx, 6, rev, fmt_cell_currency)
    ws_dash.write(r_idx, 7, cogs, fmt_cell_currency)
    ws_dash.write(r_idx, 8, profit, fmt_cell_currency)
    ws_dash.write_formula(r_idx, 9, f"=I{r_idx+1}/G{r_idx+1}", fmt_cell_pct)

# Category Total Row (Row 22, index 21)
ws_dash.write(21, 3, "Total", fmt_total_row_label)
ws_dash.write_formula(21, 4, "=SUM(E18:E21)", fmt_total_row_int)
ws_dash.write_formula(21, 5, "=SUM(F18:F21)", fmt_total_row_int)
ws_dash.write_formula(21, 6, "=SUM(G18:G21)", fmt_total_row_currency)
ws_dash.write_formula(21, 7, "=SUM(H18:H21)", fmt_total_row_currency)
ws_dash.write_formula(21, 8, "=SUM(I18:I21)", fmt_total_row_currency)
ws_dash.write_formula(21, 9, "=I22/G22", fmt_total_row_pct)

# Segment Summary (Rows 24 - 28)
ws_dash.write('B24', "Customer Segment Summary", workbook.add_format({'bold': True, 'font_size': 11}))
for c_idx, h in enumerate(["Segment", "Customers", "Orders", "Revenue", "Profit", "Margin %"]):
    ws_dash.write(24, c_idx + 3, h, fmt_tbl_header)

for r_idx, row in enumerate(segment_rows, start=25):
    seg, custs, ords, rev, profit = row
    ws_dash.write(r_idx, 3, seg, fmt_cell_text)
    ws_dash.write(r_idx, 4, custs, fmt_cell_int)
    ws_dash.write(r_idx, 5, ords, fmt_cell_int)
    ws_dash.write(r_idx, 6, rev, fmt_cell_currency)
    ws_dash.write(r_idx, 7, profit, fmt_cell_currency)
    ws_dash.write_formula(r_idx, 8, f"=H{r_idx+1}/G{r_idx+1}", fmt_cell_pct)

# Regional Summary (Rows 30 - 34)
ws_dash.write('B30', "Regional Performance Summary", workbook.add_format({'bold': True, 'font_size': 11}))
for c_idx, h in enumerate(["Region", "Orders", "Revenue", "Profit", "AOV"]):
    ws_dash.write(30, c_idx + 3, h, fmt_tbl_header)

for r_idx, row in enumerate(regional_rows, start=31):
    reg, ords, rev, profit = row
    ws_dash.write(r_idx, 3, reg, fmt_cell_text)
    ws_dash.write(r_idx, 4, ords, fmt_cell_int)
    ws_dash.write(r_idx, 5, rev, fmt_cell_currency)
    ws_dash.write(r_idx, 6, profit, fmt_cell_currency)
    ws_dash.write_formula(r_idx, 7, f"=F{r_idx+1}/E{r_idx+1}", fmt_cell_currency)

# --- DASHBOARD CHARTS ---
# Chart 1: Category Revenue & Profit
chart_cat = workbook.add_chart({'type': 'column'})
chart_cat.add_series({
    'name': 'Revenue',
    'categories': ['Executive Dashboard', 17, 3, 20, 3],
    'values': ['Executive Dashboard', 17, 6, 20, 6],
    'fill': {'color': '#1B365D'},
})
chart_cat.add_series({
    'name': 'Gross Profit',
    'categories': ['Executive Dashboard', 17, 3, 20, 3],
    'values': ['Executive Dashboard', 17, 8, 20, 8],
    'fill': {'color': '#059669'},
})
chart_cat.set_title({'name': 'Revenue vs. Gross Profit by Category'})
chart_cat.set_y_axis({'name': 'Amount ($)', 'major_gridlines': {'visible': True}})
chart_cat.set_legend({'position': 'top'})
chart_cat.set_size({'width': 480, 'height': 270})
ws_dash.insert_chart('B37', chart_cat)

# Chart 2: Customer Segment Revenue Share
chart_seg = workbook.add_chart({'type': 'doughnut'})
chart_seg.add_series({
    'name': 'Segment Revenue',
    'categories': ['Executive Dashboard', 25, 3, 27, 3],
    'values': ['Executive Dashboard', 25, 6, 27, 6],
    'points': [
        {'fill': {'color': '#1E3A8A'}},
        {'fill': {'color': '#3B82F6'}},
        {'fill': {'color': '#93C5FD'}},
    ]
})
chart_seg.set_title({'name': 'Revenue Share by Customer Segment'})
chart_seg.set_size({'width': 360, 'height': 270})
ws_dash.insert_chart('G37', chart_seg)

# Chart 3: Regional Revenue & AOV
chart_reg = workbook.add_chart({'type': 'bar'})
chart_reg.add_series({
    'name': 'Regional Revenue',
    'categories': ['Executive Dashboard', 31, 3, 34, 3],
    'values': ['Executive Dashboard', 31, 5, 34, 5],
    'fill': {'color': '#2563EB'}
})
chart_reg.set_title({'name': 'Total Revenue by Geographic Region'})
chart_reg.set_x_axis({'name': 'Revenue ($)'})
chart_reg.set_size({'width': 420, 'height': 270})
ws_dash.insert_chart('K37', chart_reg)


# =============================================================
# SHEET 2: Monthly & Category Analysis
# =============================================================
ws_month = workbook.add_worksheet("Monthly & Category Trends")
ws_month.set_tab_color("#2563EB")
ws_month.hide_gridlines(0)
ws_month.set_column('A:A', 3)
ws_month.set_column('B:G', 16)

ws_month.write('B2', "Monthly Performance Trends (2023 - 2024)", fmt_title)
ws_month.write('B3', "Detailed month-over-month sales, COGS, gross profit and margins", fmt_subtitle)

headers_m = ["Month", "Orders", "Revenue", "COGS", "Gross Profit", "Profit Margin %"]
for idx, h in enumerate(headers_m):
    ws_month.write(4, idx + 1, h, fmt_tbl_header)

start_row_m = 5
for i, row in enumerate(monthly_rows):
    r_idx = start_row_m + i
    m_lbl, ords, rev, cogs, profit = row
    ws_month.write(r_idx, 1, m_lbl, fmt_cell_center)
    ws_month.write(r_idx, 2, ords, fmt_cell_int)
    ws_month.write(r_idx, 3, rev, fmt_cell_currency)
    ws_month.write(r_idx, 4, cogs, fmt_cell_currency)
    ws_month.write_formula(r_idx, 5, f"=D{r_idx+1}-E{r_idx+1}", fmt_cell_currency)
    ws_month.write_formula(r_idx, 6, f"=F{r_idx+1}/D{r_idx+1}", fmt_cell_pct)

end_row_m = start_row_m + len(monthly_rows)
# Total row
ws_month.write(end_row_m, 1, "Total", fmt_total_row_label)
ws_month.write_formula(end_row_m, 2, f"=SUM(C{start_row_m+1}:C{end_row_m})", fmt_total_row_int)
ws_month.write_formula(end_row_m, 3, f"=SUM(D{start_row_m+1}:D{end_row_m})", fmt_total_row_currency)
ws_month.write_formula(end_row_m, 4, f"=SUM(E{start_row_m+1}:E{end_row_m})", fmt_total_row_currency)
ws_month.write_formula(end_row_m, 5, f"=SUM(F{start_row_m+1}:F{end_row_m})", fmt_total_row_currency)
ws_month.write_formula(end_row_m, 6, f"=F{end_row_m+1}/D{end_row_m+1}", fmt_total_row_pct)

# Monthly Trend Line Chart
chart_month = workbook.add_chart({'type': 'line'})
chart_month.add_series({
    'name': 'Monthly Revenue',
    'categories': ['Monthly & Category Trends', start_row_m, 1, end_row_m - 1, 1],
    'values': ['Monthly & Category Trends', start_row_m, 3, end_row_m - 1, 3],
    'line': {'color': '#1E3A8A', 'width': 2.25},
    'marker': {'type': 'circle', 'size': 5, 'fill': {'color': '#1E3A8A'}}
})
chart_month.add_series({
    'name': 'Monthly Gross Profit',
    'categories': ['Monthly & Category Trends', start_row_m, 1, end_row_m - 1, 1],
    'values': ['Monthly & Category Trends', start_row_m, 5, end_row_m - 1, 5],
    'line': {'color': '#059669', 'width': 2.25},
    'marker': {'type': 'square', 'size': 5, 'fill': {'color': '#059669'}}
})
chart_month.set_title({'name': '24-Month Revenue and Gross Profit Trajectory'})
chart_month.set_x_axis({'name': 'Year-Month'})
chart_month.set_y_axis({'name': 'Amount ($)', 'major_gridlines': {'visible': True}})
chart_month.set_legend({'position': 'top'})
chart_month.set_size({'width': 780, 'height': 380})
ws_month.insert_chart('I5', chart_month)


# =============================================================
# SHEET 3: Customer & Regional Analysis
# =============================================================
ws_cust = workbook.add_worksheet("Customer & Regional Insights")
ws_cust.set_tab_color("#059669")
ws_cust.hide_gridlines(0)
ws_cust.set_column('A:A', 3)
ws_cust.set_column('B:C', 18)
ws_cust.set_column('D:I', 15)

ws_cust.write('B2', "Customer Segmentation & Regional Analysis", fmt_title)
ws_cust.write('B3', "Customer Lifetime Value, Repeat Purchase Rates, and Regional AOV", fmt_subtitle)

# Table 1: Repeat vs One-Time Customers
ws_cust.write('B5', "Customer Retention Profile", workbook.add_format({'bold': True, 'font_size': 11}))
headers_ret = ["Customer Group", "Count", "% Customers", "Revenue", "% Revenue", "Avg Revenue / Cust"]
for idx, h in enumerate(headers_ret):
    ws_cust.write(5, idx + 1, h, fmt_tbl_header)

ws_cust.write(6, 1, "One-time Customer", fmt_cell_text)
ws_cust.write(6, 2, 32, fmt_cell_int)
ws_cust.write(6, 3, 0.1306, fmt_cell_pct)
ws_cust.write(6, 4, 6316.07, fmt_cell_currency)
ws_cust.write(6, 5, 0.0361, fmt_cell_pct)
ws_cust.write_formula(6, 6, "=E7/C7", fmt_cell_currency)

ws_cust.write(7, 1, "Repeat Customer (2+ Orders)", fmt_cell_text)
ws_cust.write(7, 2, 213, fmt_cell_int)
ws_cust.write(7, 3, 0.8694, fmt_cell_pct)
ws_cust.write(7, 4, 168553.24, fmt_cell_currency)
ws_cust.write(7, 5, 0.9639, fmt_cell_pct)
ws_cust.write_formula(7, 6, "=E8/C8", fmt_cell_currency)

# Total
ws_cust.write(8, 1, "Total", fmt_total_row_label)
ws_cust.write_formula(8, 2, "=SUM(C7:C8)", fmt_total_row_int)
ws_cust.write_formula(8, 3, "=SUM(D7:D8)", fmt_total_row_pct)
ws_cust.write_formula(8, 4, "=SUM(E7:E8)", fmt_total_row_currency)
ws_cust.write_formula(8, 5, "=SUM(F7:F8)", fmt_total_row_pct)
ws_cust.write_formula(8, 6, "=E9/C9", fmt_total_row_currency)

# Table 2: Top 10 VIP Customers
ws_cust.write('B11', "Top 10 VIP Customers (by Lifetime Spend)", workbook.add_format({'bold': True, 'font_size': 11}))
headers_vip = ["ID", "Customer Name", "Segment", "Region", "Orders", "Units", "Total Spend", "Profit Contributed"]
for idx, h in enumerate(headers_vip):
    ws_cust.write(11, idx + 1, h, fmt_tbl_header)

for i, v in enumerate(vip_rows):
    r_idx = 12 + i
    cid, name, seg, reg, ords, units, spent, prof = v
    ws_cust.write(r_idx, 1, cid, fmt_cell_center)
    ws_cust.write(r_idx, 2, name, fmt_cell_text)
    ws_cust.write(r_idx, 3, seg, fmt_cell_text)
    ws_cust.write(r_idx, 4, reg, fmt_cell_text)
    ws_cust.write(r_idx, 5, ords, fmt_cell_int)
    ws_cust.write(r_idx, 6, units, fmt_cell_int)
    ws_cust.write(r_idx, 7, spent, fmt_cell_currency)
    ws_cust.write(r_idx, 8, prof, fmt_cell_currency)


# =============================================================
# SHEET 4: Orders_Clean_Data (Consolidated Fact/Dimension Table)
# =============================================================
ws_data = workbook.add_worksheet("Orders_Clean_Data")
ws_data.set_tab_color("#475569")
ws_data.hide_gridlines(0)

cols_info = [
    ("Order ID", 10, fmt_cell_int),
    ("Order Date", 12, fmt_cell_center),
    ("Year", 8, fmt_cell_center),
    ("Year-Month", 11, fmt_cell_center),
    ("Customer ID", 12, fmt_cell_int),
    ("Customer Name", 20, fmt_cell_text),
    ("Customer Segment", 16, fmt_cell_text),
    ("Region", 12, fmt_cell_text),
    ("State", 8, fmt_cell_center),
    ("Product ID", 11, fmt_cell_int),
    ("Product Name", 32, fmt_cell_text),
    ("Category", 16, fmt_cell_text),
    ("Sub-Category", 18, fmt_cell_text),
    ("Quantity", 10, fmt_cell_int),
    ("Unit Cost", 12, fmt_cell_currency),
    ("Unit Price", 12, fmt_cell_currency),
    ("Discount", 10, fmt_cell_pct),
    ("Line Revenue", 14, fmt_cell_currency),
    ("COGS", 12, fmt_cell_currency),
    ("Gross Profit", 14, fmt_cell_currency),
    ("Margin %", 11, fmt_cell_pct),
]

for col_idx, (col_name, col_width, _) in enumerate(cols_info):
    ws_data.set_column(col_idx, col_idx, col_width)
    ws_data.write(0, col_idx, col_name, fmt_tbl_header)

ws_data.freeze_panes(1, 2)

for r_idx, row in enumerate(clean_data_rows, start=1):
    excel_row_num = r_idx + 1
    # Unpack database values
    (oid, odate, oyear, oym, cid, cname, cseg, creg, cstate,
     pid, pname, pcat, psub, qty, ucost, uprice, disc,
     rev, cogs, profit, margin) = row
    
    ws_data.write(r_idx, 0, oid, fmt_cell_int)
    ws_data.write(r_idx, 1, odate, fmt_cell_center)
    ws_data.write(r_idx, 2, oyear, fmt_cell_center)
    ws_data.write(r_idx, 3, oym, fmt_cell_center)
    ws_data.write(r_idx, 4, cid, fmt_cell_int)
    ws_data.write(r_idx, 5, cname, fmt_cell_text)
    ws_data.write(r_idx, 6, cseg, fmt_cell_text)
    ws_data.write(r_idx, 7, creg, fmt_cell_text)
    ws_data.write(r_idx, 8, cstate, fmt_cell_center)
    ws_data.write(r_idx, 9, pid, fmt_cell_int)
    ws_data.write(r_idx, 10, pname, fmt_cell_text)
    ws_data.write(r_idx, 11, pcat, fmt_cell_text)
    ws_data.write(r_idx, 12, psub, fmt_cell_text)
    ws_data.write(r_idx, 13, qty, fmt_cell_int)
    ws_data.write(r_idx, 14, ucost, fmt_cell_currency)
    ws_data.write(r_idx, 15, uprice, fmt_cell_currency)
    ws_data.write(r_idx, 16, disc, fmt_cell_pct)
    
    # Use real Excel formulas for calculations to impress recruiters!
    ws_data.write_formula(r_idx, 17, f"=N{excel_row_num}*P{excel_row_num}*(1-Q{excel_row_num})", fmt_cell_currency)
    ws_data.write_formula(r_idx, 18, f"=N{excel_row_num}*O{excel_row_num}", fmt_cell_currency)
    ws_data.write_formula(r_idx, 19, f"=R{excel_row_num}-S{excel_row_num}", fmt_cell_currency)
    ws_data.write_formula(r_idx, 20, f"=T{excel_row_num}/R{excel_row_num}", fmt_cell_pct)


# =============================================================
# SHEET 5: Products_Catalog
# =============================================================
ws_prod = workbook.add_worksheet("Products_Catalog")
ws_prod.set_tab_color("#64748B")
ws_prod.hide_gridlines(0)
ws_prod.set_column('A:A', 12)
ws_prod.set_column('B:B', 34)
ws_prod.set_column('C:D', 18)
ws_prod.set_column('E:G', 14)

prod_headers = ["Product ID", "Product Name", "Category", "Sub-Category", "Unit Cost", "Unit Price", "Standard Margin"]
for idx, h in enumerate(prod_headers):
    ws_prod.write(0, idx, h, fmt_tbl_header)

ws_prod.freeze_panes(1, 1)

for r_idx, p in enumerate(catalog_rows, start=1):
    pid, pname, pcat, psub, ucost, uprice = p
    ws_prod.write(r_idx, 0, pid, fmt_cell_int)
    ws_prod.write(r_idx, 1, pname, fmt_cell_text)
    ws_prod.write(r_idx, 2, pcat, fmt_cell_text)
    ws_prod.write(r_idx, 3, psub, fmt_cell_text)
    ws_prod.write(r_idx, 4, ucost, fmt_cell_currency)
    ws_prod.write(r_idx, 5, uprice, fmt_cell_currency)
    ws_prod.write_formula(r_idx, 6, f"=(F{r_idx+1}-E{r_idx+1})/F{r_idx+1}", fmt_cell_pct)


# =============================================================
# SHEET 6: Customers_Master
# =============================================================
ws_cm = workbook.add_worksheet("Customers_Master")
ws_cm.set_tab_color("#64748B")
ws_cm.hide_gridlines(0)
ws_cm.set_column('A:A', 14)
ws_cm.set_column('B:C', 16)
ws_cm.set_column('D:D', 28)
ws_cm.set_column('E:E', 18)
ws_cm.set_column('F:H', 15)
ws_cm.set_column('I:I', 14)

cust_headers = ["Customer ID", "First Name", "Last Name", "Email", "Segment", "City", "State", "Region", "Signup Date"]
for idx, h in enumerate(cust_headers):
    ws_cm.write(0, idx, h, fmt_tbl_header)

ws_cm.freeze_panes(1, 1)

for r_idx, c in enumerate(customer_master_rows, start=1):
    cid, fn, ln, email, seg, city, state, reg, sdate = c
    ws_cm.write(r_idx, 0, cid, fmt_cell_int)
    ws_cm.write(r_idx, 1, fn, fmt_cell_text)
    ws_cm.write(r_idx, 2, ln, fmt_cell_text)
    ws_cm.write(r_idx, 3, email, fmt_cell_text)
    ws_cm.write(r_idx, 4, seg, fmt_cell_text)
    ws_cm.write(r_idx, 5, city, fmt_cell_text)
    ws_cm.write(r_idx, 6, state, fmt_cell_center)
    ws_cm.write(r_idx, 7, reg, fmt_cell_text)
    ws_cm.write(r_idx, 8, sdate, fmt_cell_center)

workbook.close()
print(f"SUCCESS: Excel Portfolio Workbook generated at {EXCEL_PATH}")
