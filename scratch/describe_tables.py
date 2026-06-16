import json
import pymysql

with open('config.json') as f:
    config = json.load(f)

conn = pymysql.connect(
    host=config.get('db_host', 'localhost'),
    port=int(config.get('db_port', 3306)),
    user=config.get('db_user', 'root'),
    password=config.get('db_pass', ''),
    database=config.get('db_name', 'nextcare_db')
)

c = conn.cursor()
tables = [
    'lab_samples', 'lab_tests', 'lis_ddt', 'lab_reports', 
    'patient_consents', 'tube_types', 'consent_templates', 
    'lis_microbiology_results'
]

for t in tables:
    try:
        c.execute(f"DESCRIBE `{t}`")
        cols = [r[0] for r in c.fetchall()]
        print(f"{t.upper()}: {cols}")
    except Exception as e:
        print(f"Error {t}: {e}")

conn.close()
