import pymysql
import json
import datetime

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

# Get all patient IDs
cur.execute("SELECT id FROM patients")
patient_ids = [r['id'] for r in cur.fetchall()]

print(f"Testing {len(patient_ids)} patients...")

for pid in patient_ids:
    # 1. Test appointments query
    try:
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
            WHERE a.patient_id = %s
            ORDER BY a.appointment_datetime DESC
        """, (pid,))
        apps = cur.fetchall()
    except Exception as e:
        print(f"[ERROR] Appointments for patient {pid}: {e}")

    # 2. Test reports query
    try:
        cur.execute("""
            SELECT DISTINCT lr.id, lr.released_at, 'lis' as type, 'Analisi di Laboratorio' as service_name
            FROM lab_reports lr
            JOIN lab_samples ls ON lr.session_uid = ls.session_uid
            WHERE ls.patient_id = %s AND lr.status = 'official'
        """, (pid,))
        lis = cur.fetchall()
        
        cur.execute("""
            SELECT rs.id, rs.signed_at as released_at, 'ris' as type, s.name as service_name
            FROM radiology_studies rs
            JOIN medical_services s ON rs.service_id = s.id
            WHERE rs.patient_id = %s AND rs.status = 'completed'
        """, (pid,))
        ris = cur.fetchall()
        
        rows = list(lis) + list(ris)
        for r in rows:
            if r['released_at']:
                # Test the string conversion
                str(r['released_at'])
    except Exception as e:
        print(f"[ERROR] Reports for patient {pid}: {e}")

    # 3. Test invoices query
    try:
        cur.execute("""
            SELECT i.*, i.issue_date AS invoice_date, i.amount_due AS amount
            FROM invoices i
            LEFT JOIN admissions adm ON i.admission_id = adm.id
            LEFT JOIN appointments app ON i.appointment_id = app.id
            WHERE adm.patient_id = %s OR app.patient_id = %s
            ORDER BY i.issue_date DESC
        """, (pid, pid))
        invs = cur.fetchall()
    except Exception as e:
        print(f"[ERROR] Invoices for patient {pid}: {e}")

print("Testing completed.")
conn.close()
