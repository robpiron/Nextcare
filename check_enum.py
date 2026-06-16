from server import get_db_connection

conn = get_db_connection()
if conn:
    with conn.cursor() as cur:
        cur.execute("SHOW COLUMNS FROM `lab_samples` LIKE 'status'")
        row = cur.fetchone()
        print(row)
    conn.close()
