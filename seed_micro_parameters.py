import re
import json
import pymysql

with open(r"C:\Users\robpiron\.gemini\antigravity\brain\903f9250-e71f-41ba-acca-04016e91ca20\scratch\seeds_snippet.js", "r", encoding="utf-8") as f:
    js_content = f.read()

# Extract organisms
org_block = re.search(r'SEED_DATA\.ssn_microbiology_organisms\s*=\s*\[(.*?)\];', js_content, re.DOTALL).group(1)
organisms = []
for line in org_block.strip().split('\n'):
    m = re.search(r"id:\s*(\d+),\s*code:\s*'([^']*)',\s*name:\s*'([^']*)'", line)
    if m:
        organisms.append((int(m.group(1)), m.group(2), m.group(3)))

# Extract antibiotics
anti_block = re.search(r'SEED_DATA\.ssn_microbiology_antibiotics\s*=\s*\[(.*?)\];', js_content, re.DOTALL).group(1)
antibiotics = []
for line in anti_block.strip().split('\n'):
    m = re.search(r"id:\s*(\d+),\s*code:\s*'([^']*)',\s*name:\s*'([^']*)'", line)
    if m:
        antibiotics.append((int(m.group(1)), m.group(2), m.group(3)))

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

conn = pymysql.connect(
    host=config.get('db_host', 'localhost'),
    port=int(config.get('db_port', 3306)),
    user=config.get('db_user', 'root'),
    password=config.get('db_pass', ''),
    database=config.get('db_name', 'nextcare_db'),
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        cursor.execute("TRUNCATE TABLE `ssn_microbiology_organisms`;")
        cursor.execute("TRUNCATE TABLE `ssn_microbiology_antibiotics`;")
        
        # Insert organisms
        cursor.executemany(
            "INSERT INTO `ssn_microbiology_organisms` (id, code, name, active) VALUES (%s, %s, %s, 1)",
            organisms
        )
        # Insert antibiotics
        cursor.executemany(
            "INSERT INTO `ssn_microbiology_antibiotics` (id, code, name, active) VALUES (%s, %s, %s, 1)",
            antibiotics
        )
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print(f"Successfully seeded {len(organisms)} organisms and {len(antibiotics)} antibiotics in MySQL.")
    conn.commit()
finally:
    conn.close()
