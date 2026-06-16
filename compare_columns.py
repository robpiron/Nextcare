import json
import os
import pymysql

# Load config
config = {}
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Load seeds
seeds = {}
for file in ['ris_visite_services_seed.json', 'lis_services_seed.json']:
    # Let's load the app.js seed data directly by reading SEED_DATA from app.js
    pass

# A better way is to read the app.js SEED_DATA keys and structures
content = open('app.js', encoding='utf-8').read()
import re
seed_block = re.search(r'const SEED_DATA = \{(.*?)\n\};', content, re.DOTALL).group(1)
# parse keys
keys = re.findall(r'^\s*(\w+):\s*\[', seed_block, re.MULTILINE)

# Let's extract each key's list content by executing a small regex or searching
# Let's just find the first item for each table to get the keys
seed_data = {}
for k in keys:
    # find key in seed_block
    match = re.search(fr'{k}:\s*\[\s*{{(.*?)}}\s*,?\s*\]', seed_block, re.DOTALL)
    if not match:
        # try without ending bracket
        match = re.search(fr'{k}:\s*\[\s*{{(.*?)}}\s*', seed_block, re.DOTALL)
    if match:
        item_str = "{" + match.group(1).strip() + "}"
        # Convert JS object-like syntax to JSON (unquoted keys to quoted keys, remove comments)
        item_str = re.sub(r'//.*', '', item_str)
        item_str = re.sub(r'(\w+):', r'"\1":', item_str)
        # remove single quotes and replace with double
        item_str = re.sub(r"'([^']*)'", r'"\1"', item_str)
        # remove trailing commas
        item_str = re.sub(r',\s*}', '}', item_str)
        try:
            item = json.loads(item_str)
            seed_data[k] = list(item.keys())
        except Exception as e:
            # print("Failed to parse", k, item_str, str(e))
            pass

# Connect to MySQL
conn = pymysql.connect(
    host=config.get('db_host', 'localhost'),
    port=int(config.get('db_port', 3306)),
    user=config.get('db_user', 'root'),
    password=config.get('db_pass', ''),
    database=config.get('db_name', 'nextcare_db'),
    charset='utf8mb4'
)
cursor = conn.cursor()

# Get MySQL tables
cursor.execute("SHOW TABLES")
db_tables = [r[0].lower() for r in cursor.fetchall()]

print("COLUMN COMPARISON REPORT:")
for table_name, seed_keys in seed_data.items():
    if table_name.lower() in db_tables:
        cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
        db_cols = [col[0].lower() for col in cursor.fetchall()]
        missing = [k for k in seed_keys if k.lower() not in db_cols and k.lower() != 'id']
        if missing:
            print(f"Table '{table_name}' is missing columns in MySQL: {missing}")

conn.close()
