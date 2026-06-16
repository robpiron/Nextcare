import json
import pymysql

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

# We will read seed data directly from seeds_snippet.js to avoid duplicating long lists
import re
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

queries = [
    "DROP TABLE IF EXISTS `ssn_microbiology_organisms`;",
    "DROP TABLE IF EXISTS `ssn_microbiology_antibiotics`;",
    "DROP TABLE IF EXISTS `lis_microbiology_organisms`;",
    "DROP TABLE IF EXISTS `lis_microbiology_antibiotics`;",
    """
    CREATE TABLE `lis_microbiology_organisms` (
      `id` INT AUTO_INCREMENT PRIMARY KEY,
      `code` VARCHAR(50) NOT NULL UNIQUE,
      `name` VARCHAR(255) NOT NULL,
      `active` TINYINT(1) NOT NULL DEFAULT 1
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """,
    """
    CREATE TABLE `lis_microbiology_antibiotics` (
      `id` INT AUTO_INCREMENT PRIMARY KEY,
      `code` VARCHAR(50) NOT NULL UNIQUE,
      `name` VARCHAR(255) NOT NULL,
      `active` TINYINT(1) NOT NULL DEFAULT 1
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
]

try:
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        for q in queries:
            cursor.execute(q)
            
        # Seed organisms
        cursor.executemany(
            "INSERT INTO `lis_microbiology_organisms` (id, code, name, active) VALUES (%s, %s, %s, 1)",
            organisms
        )
        # Seed antibiotics
        cursor.executemany(
            "INSERT INTO `lis_microbiology_antibiotics` (id, code, name, active) VALUES (%s, %s, %s, 1)",
            antibiotics
        )
        
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print(f"Successfully renamed and seeded {len(organisms)} organisms and {len(antibiotics)} antibiotics in MySQL.")
    conn.commit()
finally:
    conn.close()
