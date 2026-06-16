import pymysql
import json

with open('config.json') as f:
    config = json.load(f)

conn = pymysql.connect(
    host=config['db_host'],
    user=config['db_user'],
    password=config['db_pass'],
    database=config['db_name'],
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()
cursor.execute("SELECT id, name FROM price_lists")
for row in cursor.fetchall():
    print(row)
conn.close()
