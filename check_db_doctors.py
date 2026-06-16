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
        print("=== Columns of 'doctors' ===")
        cursor.execute("DESCRIBE doctors")
        for row in cursor.fetchall():
            print(row)
            
        print("\n=== Columns of 'doctor_compensations_config' ===")
        cursor.execute("DESCRIBE doctor_compensations_config")
        for row in cursor.fetchall():
            print(row)
            
        print("\n=== Columns of 'doctor_calculated_compensations' ===")
        cursor.execute("DESCRIBE doctor_calculated_compensations")
        for row in cursor.fetchall():
            print(row)
finally:
    conn.close()
