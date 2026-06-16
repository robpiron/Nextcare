from server import get_db_connection
import json

conn = get_db_connection()
if conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, lis_transcoding FROM equipment WHERE id = 11")
        row = cur.fetchone()
        print(f"Type of lis_transcoding: {type(row['lis_transcoding'])}")
        print(f"Value: {row['lis_transcoding']}")
    conn.close()
