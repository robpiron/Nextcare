import json
import pymysql
import decimal
import datetime

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

def clean_db_rows(rows):
    cleaned_rows = []
    for row in rows:
        cleaned_row = {}
        for col, val in row.items():
            if val is None:
                cleaned_row[col] = None
            elif isinstance(val, decimal.Decimal):
                cleaned_row[col] = float(val)
            elif isinstance(val, (datetime.datetime, datetime.date, datetime.time)):
                cleaned_row[col] = val.isoformat()
            elif col in ['parameters', 'details', 'custom_rates', 'service_ids', 'active_days', 'updated_fields', 'values', 'package_items', 'lis_transcoding', 'profiles', 'doctor_ids', 'reporting_doctor_ids', 'antibiotics_json', 'samples_json'] and isinstance(val, str):
                try:
                    cleaned_row[col] = json.loads(val)
                except Exception:
                    cleaned_row[col] = val
            else:
                cleaned_row[col] = val
        cleaned_rows.append(cleaned_row)
    return cleaned_rows

def test_direct():
    conn = pymysql.connect(
        host=config.get('db_host', 'localhost'),
        port=int(config.get('db_port', 3306)),
        user=config.get('db_user', 'root'),
        password=config.get('db_pass', ''),
        database=config.get('db_name', 'nextcare_db'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cp_id = 1
    try:
        with conn.cursor() as cur:
            print("Fetching lab_samples...")
            cur.execute("SELECT * FROM lab_samples WHERE collection_point_id = %s", (cp_id,))
            samples = clean_db_rows(cur.fetchall())
            print(f"Found {len(samples)} samples.")
            sample_ids = [s['id'] for s in samples]
            session_uids = list(set([s['session_uid'] for s in samples if s.get('session_uid')]))
            
            print("Fetching tests...")
            tests = []
            if sample_ids:
                format_strings = ','.join(['%s'] * len(sample_ids))
                cur.execute(f"SELECT * FROM lab_tests WHERE sample_id IN ({format_strings})", tuple(sample_ids))
                tests = clean_db_rows(cur.fetchall())
            print(f"Found {len(tests)} tests.")
                
            print("Fetching LIS DDT...")
            cur.execute("SELECT * FROM lis_ddt WHERE collection_point_id = %s", (cp_id,))
            ddts = clean_db_rows(cur.fetchall())
            print(f"Found {len(ddts)} ddts.")
            
            print("Fetching lab_reports...")
            reports = []
            if session_uids:
                format_strings = ','.join(['%s'] * len(session_uids))
                cur.execute(f"SELECT * FROM lab_reports WHERE session_uid IN ({format_strings})", tuple(session_uids))
                reports = clean_db_rows(cur.fetchall())
            print(f"Found {len(reports)} reports.")
                
            print("Fetching invoices...")
            cur.execute("SELECT * FROM invoices WHERE collection_point_id = %s", (cp_id,))
            invoices = clean_db_rows(cur.fetchall())
            print(f"Found {len(invoices)} invoices.")
            
            print("Fetching patient_ids...")
            patient_ids = list(set([s['patient_id'] for s in samples if s.get('patient_id')]))
            patients = []
            consents = []
            if patient_ids:
                format_strings = ','.join(['%s'] * len(patient_ids))
                cur.execute(f"SELECT * FROM patients WHERE id IN ({format_strings})", tuple(patient_ids))
                patients = clean_db_rows(cur.fetchall())
                
                print("Fetching patient_consents...")
                cur.execute(f"SELECT * FROM patient_consents WHERE patient_id IN ({format_strings})", tuple(patient_ids))
                consents = clean_db_rows(cur.fetchall())
            print(f"Found {len(patients)} patients and {len(consents)} consents.")
                
            print("Fetching medical_services...")
            cur.execute("SELECT * FROM medical_services WHERE type = 'lis'")
            services = clean_db_rows(cur.fetchall())
            print(f"Found {len(services)} services.")
            
            print("Fetching LIS collection points...")
            cur.execute("SELECT id, code, name, address, phone, email, invoice_separate, invoice_prefix, invoice_next_num, billing_type FROM lis_collection_points")
            points = clean_db_rows(cur.fetchall())
            print(f"Found {len(points)} points.")
            
            print("Fetching tube_types...")
            cur.execute("SELECT * FROM tube_types")
            tube_types = clean_db_rows(cur.fetchall())
            print(f"Found {len(tube_types)} tube_types.")
            
            print("Fetching consent_templates...")
            cur.execute("SELECT * FROM consent_templates")
            templates = clean_db_rows(cur.fetchall())
            print(f"Found {len(templates)} consent_templates.")
            
            print("Fetching LIS microbiology results...")
            micro_results = []
            if tests:
                test_ids = [t['id'] for t in tests]
                format_strings = ','.join(['%s'] * len(test_ids))
                cur.execute(f"SELECT * FROM lis_microbiology_results WHERE test_id IN ({format_strings})", tuple(test_ids))
                micro_results = clean_db_rows(cur.fetchall())
            print(f"Found {len(micro_results)} micro_results.")
            
            data = {
                "patients": patients,
                "samples": samples,
                "tests": tests,
                "invoices": invoices,
                "lis_ddt": ddts,
                "lab_reports": reports,
                "patient_consents": consents,
                "services": services,
                "collection_points": points,
                "tube_types": tube_types,
                "consent_templates": templates,
                "lis_microbiology_results": micro_results
            }
            res = {"success": True, "data": data}
            json.dumps(res)
            print("Successfully serialized data!")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    test_direct()
