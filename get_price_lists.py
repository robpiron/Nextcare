import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="nextcare"
)
cursor = conn.cursor()
cursor.execute("SELECT id, name, discount_percentage FROM price_lists")
for row in cursor.fetchall():
    print(row)
conn.close()
