import json
import pymysql
import os

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
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
tables = [r[0] for r in cursor.fetchall()]

print("MySQL tables and row counts:")
for t in tables:
    cursor.execute(f"SELECT COUNT(*) FROM `{t}`")
    count = cursor.fetchone()[0]
    print(f"  {t}: {count} rows")

conn.close()
