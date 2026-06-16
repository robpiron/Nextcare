import json
import pymysql

# Load database config
with open('config.json', 'r') as f:
    config = json.load(f)

# Connect to database
conn = pymysql.connect(
    host=config['db_host'],
    port=config.get('db_port', 3306),
    user=config['db_user'],
    password=config['db_pass'],
    database=config['db_name']
)

try:
    with conn.cursor() as cursor:
        print("=== Columns of 'radiology_studies' ===")
        cursor.execute("DESCRIBE radiology_studies")
        for row in cursor.fetchall():
            print(row)
finally:
    conn.close()
