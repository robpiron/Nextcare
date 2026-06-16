import pymysql
import json

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

conn = pymysql.connect(
    host=config.get('db_host', 'localhost'),
    port=int(config.get('db_port', 3306)),
    user=config.get('db_user', 'root'),
    password=config.get('db_pass', ''),
    database=config.get('db_name', 'nextcare_db'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cur = conn.cursor()

try:
    # Test appointments
    cur.execute("""
        SELECT a.id, a.patient_id, a.doctor_id, a.appointment_datetime AS scheduled_at, a.status, a.notes,
               CONCAT(st.first_name, ' ', st.last_name) as doctor_name,
               (
                   SELECT GROUP_CONCAT(s.name SEPARATOR ', ')
                   FROM appointment_services aps
                   JOIN medical_services s ON aps.service_id = s.id
                   WHERE aps.appointment_id = a.id
               ) AS service_name
        FROM appointments a
        LEFT JOIN doctors d ON a.doctor_id = d.id
        LEFT JOIN staff st ON d.staff_id = st.id
        WHERE a.patient_id = 1
        ORDER BY a.appointment_datetime DESC
    """)
    print("Appointments Success. Count:", len(cur.fetchall()))
except Exception as e:
    print("Appointments SQL Error:", e)

try:
    # Test LIS reports
    cur.execute("""
        SELECT DISTINCT lr.id, lr.released_at, 'lis' as type, 'Analisi di Laboratorio' as service_name
        FROM lab_reports lr
        JOIN lab_samples ls ON lr.session_uid = ls.session_uid
        WHERE ls.patient_id = 1 AND lr.status = 'official'
    """)
    print("LIS Reports Success. Count:", len(cur.fetchall()))
except Exception as e:
    print("LIS Reports SQL Error:", e)

try:
    # Test RIS reports
    cur.execute("""
        SELECT rs.id, rs.signed_at as released_at, 'ris' as type, s.name as service_name
        FROM radiology_studies rs
        JOIN medical_services s ON rs.service_id = s.id
        WHERE rs.patient_id = 1 AND rs.status = 'completed'
    """)
    print("RIS Reports Success. Count:", len(cur.fetchall()))
except Exception as e:
    print("RIS Reports SQL Error:", e)

conn.close()
