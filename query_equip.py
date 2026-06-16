import json
from server import get_db_connection

conn = get_db_connection()
if conn:
    with conn.cursor() as cur:
        cur.execute("SELECT id, name, type, status, lis_interface_type, lis_file_format, lis_socket_port, lis_socket_format, lis_simulator_active FROM equipment")
        rows = cur.fetchall()
        for r in rows:
            print(r)
    conn.close()
