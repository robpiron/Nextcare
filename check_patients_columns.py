import pymysql
import json

with open('config.json') as f:
    config = json.load(f)

conn = pymysql.connect(
    host=config['db_host'],
    user=config['db_user'],
    password=config['db_pass'],
    database=config['db_name']
)
cursor = conn.cursor()
cursor.execute("DESCRIBE patients")
for row in cursor.fetchall():
    print(row)
conn.close()
