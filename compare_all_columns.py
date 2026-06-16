import json
import os
import pymysql
import re

# Load config
config = {}
if os.path.exists("config.json"):
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)

# Read app.js
content = open('app.js', encoding='utf-8').read()

# Let's extract SEED_DATA block using a JS-like brace matching since it might be large
# Find starting index of const SEED_DATA =
start_match = re.search(r'const\s+SEED_DATA\s*=\s*\{', content)
if start_match:
    start_idx = start_match.end() - 1
    # Trace curly braces to find the end of SEED_DATA
    brace_count = 1
    end_idx = start_idx + 1
    while brace_count > 0 and end_idx < len(content):
        char = content[end_idx]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        end_idx += 1
    
    seed_block = content[start_idx:end_idx]
    
    # Write a quick regex to find all array definitions in SEED_DATA
    # e.g., staff: [ ... ], or audit_logs: [ ... ]
    # We can search for keys
    array_matches = re.finditer(r'^\s*(\w+):\s*\[', seed_block, re.MULTILINE)
    
    seed_data_keys = {}
    for am in array_matches:
        key_name = am.group(1)
        # Find the end of this array
        arr_start = am.end() - 1
        arr_brace_count = 1
        arr_end = arr_start + 1
        while arr_brace_count > 0 and arr_end < len(seed_block):
            c = seed_block[arr_end]
            if c == '[':
                arr_brace_count += 1
            elif c == ']':
                arr_brace_count -= 1
            arr_end += 1
        
        arr_content = seed_block[arr_start:arr_end]
        # Find all objects within this array contents: { ... }
        obj_matches = re.findall(r'\{([^{}]*)\}', arr_content)
        
        union_keys = set()
        for obj_str in obj_matches:
            # Clean obj_str and extract keys
            # Format: key: value, key2: value2
            # Let's extract words followed by colon
            words = re.findall(r'(\w+):\s*', obj_str)
            for w in words:
                union_keys.add(w)
        
        if union_keys:
            seed_data_keys[key_name] = sorted(list(union_keys))

    print("Parsed SEED_DATA keys from app.js:")
    for k, v in seed_data_keys.items():
        print(f"  {k}: {v}")

    # Connect to MySQL and check columns
    if config.get('db_host'):
        try:
            conn = pymysql.connect(
                host=config.get('db_host', 'localhost'),
                port=int(config.get('db_port', 3306)),
                user=config.get('db_user', 'root'),
                password=config.get('db_pass', ''),
                database=config.get('db_name', 'nextcare_db'),
                charset='utf8mb4'
            )
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES")
            db_tables = [r[0].lower() for r in cursor.fetchall()]

            print("\nCOLUMN COMPARISON WITH MYSQL:")
            for table_name, seed_keys in seed_data_keys.items():
                if table_name.lower() in db_tables:
                    cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                    db_cols = [col[0].lower() for col in cursor.fetchall()]
                    missing = [k for k in seed_keys if k.lower() not in db_cols and k.lower() != 'id']
                    if missing:
                        print(f"Table '{table_name}' is missing columns in MySQL: {missing}")
                else:
                    print(f"Table '{table_name}' does not exist in MySQL database!")
            conn.close()
        except Exception as e:
            print("Failed to connect or query MySQL:", str(e))
else:
    print("Could not find SEED_DATA in app.js")
