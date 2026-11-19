"""
NovaMart Retail Data Generator & Database Loader
Generates realistic, balanced synthetic data, exports to CSV,
creates the SQLite database, and runs integrity validation checks.
"""

import sqlite3
import csv
import random
from datetime import datetime, timedelta
from pathlib import Path

# Fix random seed for full reproducibility
random.seed(42)

BASE_DIR = Path(r"w:\projectsql")
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
DB_PATH = BASE_DIR / "data" / "novamart.db"
SCHEMA_PATH = BASE_DIR / "sql" / "01_schema.sql"

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------
# 1. Customers Generation (250 customers)
# -------------------------------------------------------------
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Timothy", "Deborah", "Ronald", "Stephanie", "Edward", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Gregory", "Christine", "Frank", "Debra",
    "Alexander", "Rachel", "Raymond", "Catherine", "Patrick", "Carolyn", "Jack", "Janet"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson"
]

REGIONS = {
    "East": [("New York", "NY"), ("Boston", "MA"), ("Philadelphia", "PA"), ("Newark", "NJ")],
    "West": [("Los Angeles", "CA"), ("San Francisco", "CA"), ("Seattle", "WA"), ("Phoenix", "AZ")],
    "Midwest": [("Chicago", "IL"), ("Detroit", "MI"), ("Minneapolis", "MN"), ("Columbus", "OH")],
    "South": [("Houston", "TX"), ("Dallas", "TX"), ("Atlanta", "GA"), ("Charlotte", "NC")]
}

SEGMENTS = ["Consumer", "Corporate", "Small Business"]
SEGMENT_WEIGHTS = [0.55, 0.25, 0.20]

customers = []
customer_ids = list(range(101, 351)) # 250 customers

for cid in customer_ids:
    fn = random.choice(FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    email = f"{fn.lower()}.{ln.lower()}{cid}@example.com"
    seg = random.choices(SEGMENTS, weights=SEGMENT_WEIGHTS)[0]
    region = random.choice(list(REGIONS.keys()))
    city, state = random.choice(REGIONS[region])
    # Signup date between 2022-01-01 and 2023-11-30
    start_date = datetime(2022, 1, 1)
    random_days = random.randint(0, 700)
    signup_date = (start_date + timedelta(days=random_days)).strftime("%Y-%m-%d")
    
    customers.append({
        "customer_id": cid,
        "first_name": fn,
        "last_name": ln,
        "email": email,
        "customer_segment": seg,
        "city": city,
        "state": state,
        "region": region,
        "signup_date": signup_date
    })

# -------------------------------------------------------------
# 2. Products Catalog (40 products across 4 categories)
# -------------------------------------------------------------
PRODUCTS_DATA = [
    # Electronics (10 items)
    ("Noise-Cancelling Headphones", "Electronics", "Audio", 95.00, 199.99),
    ("4K Ultra HD Monitor 27-inch", "Electronics", "Computers", 210.00, 349.99),
    ("Wireless Mechanical Keyboard", "Electronics", "Accessories", 38.00, 89.99),
    ("Ergonomic Optical Mouse", "Electronics", "Accessories", 18.00, 49.99),
    ("Portable Bluetooth Speaker", "Electronics", "Audio", 32.00, 79.99),
    ("Smart Fitness Watch", "Electronics", "Wearables", 68.00, 149.99),
    ("USB-C Multiport Docking Hub", "Electronics", "Accessories", 14.00, 39.99),
    ("1080p HD Streaming Webcam", "Electronics", "Computers", 22.00, 59.99),
    ("Heavy Duty Dual Monitor Stand", "Electronics", "Accessories", 28.00, 69.99),
    ("Fast Charge Power Bank 20000mAh", "Electronics", "Accessories", 16.00, 45.99),
    
    # Home & Kitchen (10 items)
    ("10-Piece Non-Stick Cookware Set", "Home & Kitchen", "Cookware", 55.00, 129.99),
    ("Digital Air Fryer 5.8 Qt", "Home & Kitchen", "Small Appliances", 48.00, 109.99),
    ("12-Cup Programmable Coffee Maker", "Home & Kitchen", "Small Appliances", 36.00, 89.99),
    ("Professional High-Speed Blender", "Home & Kitchen", "Small Appliances", 30.00, 79.99),
    ("Cooling Gel Memory Foam Pillow", "Home & Kitchen", "Bedding", 12.00, 34.99),
    ("Egyptian Cotton Queen Sheet Set", "Home & Kitchen", "Bedding", 24.00, 64.99),
    ("8-Piece German Steel Knife Set", "Home & Kitchen", "Cookware", 15.00, 44.99),
    ("Precision Digital Kitchen Scale", "Home & Kitchen", "Accessories", 8.00, 24.99),
    ("Touchless Stainless Steel Trash Can", "Home & Kitchen", "Home Organization", 20.00, 54.99),
    ("Rapid Boil Cordless Glass Kettle", "Home & Kitchen", "Small Appliances", 14.00, 39.99),
    
    # Apparel (10 items)
    ("Vintage Denim Jacket", "Apparel", "Outerwear", 26.00, 79.99),
    ("Men's Stretch Chino Pant", "Apparel", "Bottoms", 16.00, 49.99),
    ("Women's Merino Wool Crew Sweater", "Apparel", "Tops", 22.00, 69.99),
    ("Lightweight Athletic Running Shoes", "Apparel", "Footwear", 32.00, 89.99),
    ("Waterproof Hooded Rain Parka", "Apparel", "Outerwear", 20.00, 64.99),
    ("Organic Cotton Crew T-Shirt 3-Pack", "Apparel", "Tops", 10.00, 34.99),
    ("High-Waist Performance Leggings", "Apparel", "Bottoms", 11.00, 39.99),
    ("Genuine Leather Dress Belt", "Apparel", "Accessories", 8.50, 29.99),
    ("Cozy Fleece Pullover Hoodie", "Apparel", "Tops", 14.00, 44.99),
    ("Polarized UV400 Sunglasses", "Apparel", "Accessories", 9.00, 39.99),
    
    # Beauty & Health (10 items)
    ("Vitamin C Brightening Face Serum", "Beauty & Health", "Skincare", 6.50, 28.99),
    ("Hyaluronic Acid Daily Moisturizer", "Beauty & Health", "Skincare", 5.50, 24.99),
    ("Sonic Clean Rechargeable Toothbrush", "Beauty & Health", "Oral Care", 15.00, 49.99),
    ("Pure Moroccan Argan Hair Oil", "Beauty & Health", "Haircare", 4.80, 22.99),
    ("Broad Spectrum Mineral Sunscreen SPF 50", "Beauty & Health", "Skincare", 4.20, 19.99),
    ("Aroma Ultrasonic Essential Oil Diffuser", "Beauty & Health", "Wellness", 9.50, 32.99),
    ("Handheld Percussive Massage Gun", "Beauty & Health", "Wellness", 30.00, 89.99),
    ("Advanced Retinol Overnight Cream", "Beauty & Health", "Skincare", 7.50, 34.99),
    ("Himalayan Pink Salt Body Scrub", "Beauty & Health", "Body Care", 3.80, 18.99),
    ("Salon Professional Ionic Hair Dryer", "Beauty & Health", "Haircare", 18.00, 59.99)
]

products = []
product_lookup = {}

for idx, p in enumerate(PRODUCTS_DATA, start=1):
    prod = {
        "product_id": idx,
        "product_name": p[0],
        "category": p[1],
        "sub_category": p[2],
        "unit_cost": p[3],
        "unit_price": p[4]
    }
    products.append(prod)
    product_lookup[idx] = prod

# -------------------------------------------------------------
# 3. Orders Generation (1,200 orders across 2023 & 2024)
# -------------------------------------------------------------
SHIPPING_MODES = ["Standard", "Express", "Same Day"]
SHIPPING_WEIGHTS = [0.60, 0.30, 0.10]

PAYMENT_METHODS = ["Credit Card", "Debit Card", "PayPal", "Gift Card"]
PAYMENT_WEIGHTS = [0.55, 0.15, 0.25, 0.05]

ORDER_STATUSES = ["Completed", "Returned", "Cancelled"]
STATUS_WEIGHTS = [0.91, 0.06, 0.03]

# Create realistic order distributions:
# ~35% of customers place 1 order, ~40% place 2-4 orders, ~25% place 5-10 orders (VIPs)
customer_order_counts = {}
for cid in customer_ids:
    r = random.random()
    if r < 0.35:
        count = 1
    elif r < 0.75:
        count = random.randint(2, 4)
    else:
        count = random.randint(5, 9)
    customer_order_counts[cid] = count

# Scale/adjust total orders to exactly 1,200 orders
allocated_cids = []
for cid, cnt in customer_order_counts.items():
    allocated_cids.extend([cid] * cnt)

# If total length != 1200, resample or trim
if len(allocated_cids) > 1200:
    allocated_cids = allocated_cids[:1200]
elif len(allocated_cids) < 1200:
    diff = 1200 - len(allocated_cids)
    allocated_cids.extend(random.choices(customer_ids, k=diff))

random.shuffle(allocated_cids)

orders = []
order_items = []

order_item_counter = 1
start_date_2023 = datetime(2023, 1, 1)

DISCOUNTS = [0.0, 0.05, 0.10, 0.15, 0.20]
DISCOUNT_WEIGHTS = [0.60, 0.15, 0.12, 0.08, 0.05]

for order_idx, cid in enumerate(allocated_cids, start=1001):
    # Pick a date in 2023 or 2024 with seasonal Q4 weighting
    year = random.choices([2023, 2024], weights=[0.46, 0.54])[0]
    # Month weights (higher in Nov & Dec)
    month_weights = [0.06, 0.06, 0.07, 0.07, 0.08, 0.08, 0.08, 0.09, 0.09, 0.10, 0.14, 0.15]
    month = random.choices(list(range(1, 13)), weights=month_weights)[0]
    
    # Days in month
    if month in [1, 3, 5, 7, 8, 10, 12]:
        day = random.randint(1, 31)
    elif month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 28)
        
    order_date = f"{year}-{month:02d}-{day:02d}"
    
    ship_mode = random.choices(SHIPPING_MODES, weights=SHIPPING_WEIGHTS)[0]
    pay_method = random.choices(PAYMENT_METHODS, weights=PAYMENT_WEIGHTS)[0]
    status = random.choices(ORDER_STATUSES, weights=STATUS_WEIGHTS)[0]
    
    orders.append({
        "order_id": order_idx,
        "customer_id": cid,
        "order_date": order_date,
        "shipping_mode": ship_mode,
        "payment_method": pay_method,
        "order_status": status
    })
    
    # Order items: 1 to 4 distinct items per order
    num_items = random.choices([1, 2, 3, 4], weights=[0.50, 0.32, 0.14, 0.04])[0]
    selected_prod_ids = random.sample(list(product_lookup.keys()), num_items)
    
    for pid in selected_prod_ids:
        p_info = product_lookup[pid]
        qty = random.choices([1, 2, 3, 4], weights=[0.70, 0.20, 0.07, 0.03])[0]
        disc = random.choices(DISCOUNTS, weights=DISCOUNT_WEIGHTS)[0]
        line_total = round(qty * p_info["unit_price"] * (1.0 - disc), 2)
        
        order_items.append({
            "order_item_id": order_item_counter,
            "order_id": order_idx,
            "product_id": pid,
            "quantity": qty,
            "discount": disc,
            "line_total": line_total
        })
        order_item_counter += 1

# Sort orders chronologically
orders.sort(key=lambda x: x["order_date"])

# -------------------------------------------------------------
# 4. Export CSV Files
# -------------------------------------------------------------
def write_csv(filepath, rows, fieldnames):
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

write_csv(RAW_DATA_DIR / "customers.csv", customers, list(customers[0].keys()))
write_csv(RAW_DATA_DIR / "products.csv", products, list(products[0].keys()))
write_csv(RAW_DATA_DIR / "orders.csv", orders, list(orders[0].keys()))
write_csv(RAW_DATA_DIR / "order_items.csv", order_items, list(order_items[0].keys()))

print(f"CSVs exported to: {RAW_DATA_DIR}")
print(f"Customers: {len(customers)} | Products: {len(products)} | Orders: {len(orders)} | Order Items: {len(order_items)}")

# -------------------------------------------------------------
# 5. Create SQLite DB & Load Data
# -------------------------------------------------------------
if DB_PATH.exists():
    DB_PATH.unlink()

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    schema_sql = f.read()

cursor.executescript(schema_sql)

# Bulk insert
cursor.executemany("""
    INSERT INTO customers (customer_id, first_name, last_name, email, customer_segment, city, state, region, signup_date)
    VALUES (:customer_id, :first_name, :last_name, :email, :customer_segment, :city, :state, :region, :signup_date)
""", customers)

cursor.executemany("""
    INSERT INTO products (product_id, product_name, category, sub_category, unit_cost, unit_price)
    VALUES (:product_id, :product_name, :category, :sub_category, :unit_cost, :unit_price)
""", products)

cursor.executemany("""
    INSERT INTO orders (order_id, customer_id, order_date, shipping_mode, payment_method, order_status)
    VALUES (:order_id, :customer_id, :order_date, :shipping_mode, :payment_method, :order_status)
""", orders)

cursor.executemany("""
    INSERT INTO order_items (order_item_id, order_id, product_id, quantity, discount, line_total)
    VALUES (:order_item_id, :order_id, :product_id, :quantity, :discount, :line_total)
""", order_items)

conn.commit()

# -------------------------------------------------------------
# 6. Automated Validation Checks
# -------------------------------------------------------------
print("\n--- RUNNING VALIDATION CHECKS ---")

# Check Foreign Keys
cursor.execute("PRAGMA foreign_key_check;")
fk_violations = cursor.fetchall()
if fk_violations:
    print(f"WARNING: Foreign Key Violations Found: {fk_violations}")
else:
    print("SUCCESS: 0 Foreign Key violations! Schema integrity verified.")

# Check Counts
cursor.execute("SELECT count(*) FROM customers;")
c_cnt = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM products;")
p_cnt = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM orders;")
o_cnt = cursor.fetchone()[0]
cursor.execute("SELECT count(*) FROM order_items;")
oi_cnt = cursor.fetchone()[0]

print(f"Verified Database Row Counts: customers={c_cnt}, products={p_cnt}, orders={o_cnt}, order_items={oi_cnt}")

# Check Baseline Business Metrics on Completed Orders
cursor.execute("""
    SELECT 
        COUNT(DISTINCT o.order_id) as completed_orders,
        COUNT(DISTINCT o.customer_id) as active_customers,
        SUM(oi.quantity) as total_units_sold,
        ROUND(SUM(oi.line_total), 2) as total_revenue,
        ROUND(SUM(oi.quantity * p.unit_cost), 2) as total_cost,
        ROUND(SUM(oi.line_total - (oi.quantity * p.unit_cost)), 2) as total_profit,
        ROUND((SUM(oi.line_total - (oi.quantity * p.unit_cost)) / SUM(oi.line_total)) * 100, 2) as margin_pct,
        ROUND(SUM(oi.line_total) / COUNT(DISTINCT o.order_id), 2) as aov
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE o.order_status = 'Completed';
""")
metrics = cursor.fetchone()
print("\n--- BASELINE BUSINESS METRICS (COMPLETED ORDERS) ---")
print(f"Completed Orders:       {metrics[0]:,}")
print(f"Active Customers:       {metrics[1]:,}")
print(f"Total Units Sold:       {metrics[2]:,}")
print(f"Total Revenue:          ${metrics[3]:,.2f}")
print(f"Total Cost (COGS):      ${metrics[4]:,.2f}")
print(f"Total Profit:           ${metrics[5]:,.2f}")
print(f"Gross Margin %:         {metrics[6]}%")
print(f"Average Order Value:    ${metrics[7]:,.2f}")

conn.close()
print("\nDatabase creation and validation complete!")
