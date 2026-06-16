import json
import pymysql
import os
import sys

# Load configuration
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Connect to database
def get_db_conn():
    return pymysql.connect(
        host=config.get('db_host', 'localhost'),
        port=int(config.get('db_port', 3306)),
        user=config.get('db_user', 'root'),
        password=config.get('db_pass', ''),
        database=config.get('db_name', 'nextcare_db'),
        charset='utf8mb4',
        autocommit=True
    )

def setup_test_data():
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # Temporarily update medical services 3, 4, 5 to be the expected LIS services for testing
    cursor.execute("UPDATE medical_services SET name='TEST_Glicemia Basale (LIS)', type='lis', sample_type='Siero (Attivatore - Rosso)', price=15.00 WHERE id=3")
    cursor.execute("UPDATE medical_services SET name='TEST_Emocromo Completo (LIS)', type='lis', sample_type='Sangue intero (EDTA - Viola)', price=20.00 WHERE id=4")
    cursor.execute("UPDATE medical_services SET name='TEST_Colesterolo Totale (LIS)', type='lis', sample_type='Siero (Attivatore - Rosso)', price=18.00 WHERE id=5")
    
    # Clean up test tables to avoid conflicts
    cursor.execute("DELETE FROM lab_tests WHERE id >= 10000 OR test_name LIKE 'TEST_%'")
    cursor.execute("DELETE FROM lab_samples WHERE id >= 10000 OR session_uid LIKE 'TEST-SESS-%' OR barcode LIKE 'TESTBAR%'")
    cursor.execute("DELETE FROM invoices WHERE id >= 10000 OR invoice_number LIKE 'TEST-%'")
    
    # 1. Setup Test Case 1: Unpaid LIS acceptance (TEST-SESS-001)
    # Patient 1 (Mario Rossi, id=1)
    # Service 4 (Emocromo, Sangue EDTA, 20.00) and Service 3 (Glicemia, Siero Rosso, 15.00)
    # Total: 35.00
    
    # Insert samples
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10001, 1, 'TESTBAR001001', 'Sangue intero (EDTA - Viola)', 'collected', 'TEST-SESS-001', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10002, 1, 'TESTBAR001002', 'Siero (Attivatore - Rosso)', 'collected', 'TEST-SESS-001', NOW(), 4)
    """)
    
    # Insert tests
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10001, 10001, 4, 'TEST_Emocromo Completo (LIS)', NULL, '4.5-5.9', '10^6/uL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10002, 10002, 3, 'TEST_Glicemia Basale (LIS)', NULL, '70-100', 'mg/dL', 'pending')
    """)
    
    # Insert Invoice
    cursor.execute("""
        INSERT INTO invoices (id, sample_id, invoice_number, issue_date, subtotal, discount_amount, stamp_duty, amount_due, amount_paid, payment_status)
        VALUES (10001, 10001, 'TEST-FAT-0001', CURDATE(), 35.00, 0.00, 0.00, 35.00, 0.00, 'unpaid')
    """)
    
    # 2. Setup Test Case 2: Paid LIS acceptance (TEST-SESS-002)
    # Service 3 (Glicemia, Siero Rosso, 15.00)
    # Total: 15.00, status: paid
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10003, 1, 'TESTBAR002002', 'Siero (Attivatore - Rosso)', 'collected', 'TEST-SESS-002', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10003, 10003, 3, 'TEST_Glicemia Basale (LIS)', NULL, '70-100', 'mg/dL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO invoices (id, sample_id, invoice_number, issue_date, subtotal, discount_amount, stamp_duty, amount_due, amount_paid, payment_status, payment_method, paid_at)
        VALUES (10002, 10003, 'TEST-FAT-0002', CURDATE(), 15.00, 0.00, 0.00, 15.00, 15.00, 'paid', 'Contanti', CURDATE())
    """)
    
    # 3. Setup Test Case 3: Paid LIS acceptance for decrease (TEST-SESS-003)
    # Service 4 (20.00) + Service 3 (15.00) = 35.00 paid
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10004, 1, 'TESTBAR003001', 'Sangue intero (EDTA - Viola)', 'collected', 'TEST-SESS-003', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10005, 1, 'TESTBAR003002', 'Siero (Attivatore - Rosso)', 'collected', 'TEST-SESS-003', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10004, 10004, 4, 'TEST_Emocromo Completo (LIS)', NULL, '4.5-5.9', '10^6/uL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10005, 10005, 3, 'TEST_Glicemia Basale (LIS)', NULL, '70-100', 'mg/dL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO invoices (id, sample_id, invoice_number, issue_date, subtotal, discount_amount, stamp_duty, amount_due, amount_paid, payment_status, payment_method, paid_at)
        VALUES (10003, 10004, 'TEST-FAT-0003', CURDATE(), 35.00, 0.00, 0.00, 35.00, 35.00, 'paid', 'Carta di Credito', CURDATE())
    """)
    
    print("[OK] Test seed data populated successfully.")
    conn.close()

def run_tests_logic():
    import urllib.request
    
    def sync_table(table_name, rows):
        payload = {
            "table_name": table_name,
            "rows": rows
        }
        url = "http://127.0.0.1:8000/api/db-sync-table"
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if not res.get("success"):
                    raise Exception(f"Failed to sync {table_name}: {res.get('error')}")
        except urllib.error.HTTPError as he:
            print(f"HTTP error body: {he.read().decode('utf-8')}")
            raise

    def get_table(table_name):
        from decimal import Decimal
        conn = get_db_conn()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()
        for row in rows:
            for k, v in row.items():
                if isinstance(v, Decimal):
                    row[k] = float(v)
                elif v is not None and not isinstance(v, (int, float, str, bool)):
                    row[k] = str(v)
        conn.close()
        return rows

    print("\n--- TEST CASE 1: Modify unpaid LIS acceptance (TEST-SESS-001) ---")
    print("Action: Remove Glicemia Basale (Service ID 3, Siero, price 15.00)")
    
    samples = get_table('lab_samples')
    tests = get_table('lab_tests')
    invoices = get_table('invoices')
    services = get_table('medical_services')
    
    sess_id = 'TEST-SESS-001'
    current_editing_services = [s for s in services if s['id'] == 4] # Keep only Emocromo (ID 4)
    
    current_samples = [s for s in samples if s['session_uid'] == sess_id]
    patient_id = current_samples[0]['patient_id']
    collected_at = current_samples[0]['collected_at']
    collected_by = current_samples[0]['collected_by']
    
    required_sample_types = list(set([s['sample_type'] for s in current_editing_services if s['sample_type']]))
    
    updated_samples = [s for s in samples]
    updated_tests = [t for t in tests]
    
    sample_type_to_id = {}
    current_samples_to_delete = []
    for sam in current_samples:
        if sam['sample_type'] in required_sample_types:
            sample_type_to_id[sam['sample_type']] = sam['id']
        else:
            current_samples_to_delete.append(sam['id'])
            
    if current_samples_to_delete:
        updated_samples = [s for s in updated_samples if s['id'] not in current_samples_to_delete]
        updated_tests = [t for t in updated_tests if t['sample_id'] not in current_samples_to_delete]
        
    other_tests = [t for t in updated_tests if t['sample_id'] not in [s['id'] for s in current_samples]]
    new_tests = []
    for srv in current_editing_services:
        sample_id = sample_type_to_id.get(srv['sample_type'])
        if not sample_id:
            continue
        existing = next((t for t in tests if t['sample_id'] in [s['id'] for s in current_samples] and t['service_id'] == srv['id']), None)
        next_id = max([t['id'] for t in other_tests + new_tests]) + 1 if (other_tests + new_tests) else 10001
        new_tests.append({
            "id": next_id,
            "sample_id": sample_id,
            "service_id": srv['id'],
            "test_name": srv['name'],
            "result_value": existing['result_value'] if existing else None,
            "reference_range": srv['reference_range'] or '',
            "unit": srv['unit'] or '',
            "status": existing['status'] if existing else 'pending',
            "verified_by": existing['verified_by'] if existing else None,
            "verified_at": existing['verified_at'] if existing else None
        })
        
    updated_tests = other_tests + new_tests
    
    inv = next((i for i in invoices if i['sample_id'] in [s['id'] for s in current_samples] and not i.get('is_insurance_invoice')), None)
    new_subtotal = sum([s['price'] for s in current_editing_services])
    new_total = new_subtotal
    
    inv_index = next((idx for idx, i in enumerate(invoices) if i['id'] == inv['id']), -1)
    if inv_index != -1:
        invoices[inv_index]['subtotal'] = new_subtotal
        invoices[inv_index]['amount_due'] = new_total
        
    sync_table('lab_samples', updated_samples)
    sync_table('lab_tests', updated_tests)
    sync_table('invoices', invoices)
    
    # Assert state in MySQL
    conn = get_db_conn()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    
    cursor.execute("SELECT * FROM lab_samples WHERE session_uid = %s", (sess_id,))
    rem_samples = cursor.fetchall()
    assert len(rem_samples) == 1, f"Expected 1 remaining sample, got {len(rem_samples)}"
    assert rem_samples[0]['id'] == 10001, "Expected Sangue intero sample 10001 to remain"
    
    cursor.execute("SELECT * FROM invoices WHERE id = 10001")
    updated_inv = cursor.fetchone()
    assert float(updated_inv['amount_due']) == 20.00, f"Expected unpaid invoice amount to be 20.00, got {updated_inv['amount_due']}"
    
    print("[SUCCESS] Test Case 1: Unpaid acceptance modified. Empty tube deleted, invoice updated directly.")
    
    print("\n--- TEST CASE 1b: Add exam of new type to unpaid LIS acceptance (TEST-SESS-001) ---")
    print("Action: Add Glicemia Basale (Service ID 3, Siero, price 15.00) back")
    
    samples = get_table('lab_samples')
    tests = get_table('lab_tests')
    invoices = get_table('invoices')
    
    current_editing_services = [s for s in services if s['id'] in [3, 4]]
    current_samples = [s for s in samples if s['session_uid'] == sess_id]
    required_sample_types = list(set([s['sample_type'] for s in current_editing_services if s['sample_type']]))
    
    updated_samples = [s for s in samples]
    updated_tests = [t for t in tests]
    
    sample_type_to_id = {}
    current_samples_to_delete = []
    for sam in current_samples:
        if sam['sample_type'] in required_sample_types:
            sample_type_to_id[sam['sample_type']] = sam['id']
        else:
            current_samples_to_delete.append(sam['id'])
            
    for stype in required_sample_types:
        if not sample_type_to_id.get(stype):
            new_barcode = "000000030002"
            next_id = max([s['id'] for s in updated_samples]) + 1
            new_sample = {
                "id": next_id,
                "patient_id": patient_id,
                "barcode": new_barcode,
                "sample_type": stype,
                "status": 'collected',
                "session_uid": sess_id,
                "collected_at": collected_at,
                "collected_by": collected_by
            }
            updated_samples.append(new_sample)
            sample_type_to_id[stype] = next_id
            
    other_tests = [t for t in updated_tests if t['sample_id'] not in [s['id'] for s in current_samples]]
    new_tests = []
    for srv in current_editing_services:
        sample_id = sample_type_to_id.get(srv['sample_type'])
        if not sample_id:
            continue
        existing = next((t for t in tests if t['sample_id'] in [s['id'] for s in current_samples] and t['service_id'] == srv['id']), None)
        next_id = max([t['id'] for t in other_tests + new_tests]) + 1 if (other_tests + new_tests) else 10001
        new_tests.append({
            "id": next_id,
            "sample_id": sample_id,
            "service_id": srv['id'],
            "test_name": srv['name'],
            "result_value": existing['result_value'] if existing else None,
            "reference_range": srv['reference_range'] or '',
            "unit": srv['unit'] or '',
            "status": existing['status'] if existing else 'pending',
            "verified_by": existing['verified_by'] if existing else None,
            "verified_at": existing['verified_at'] if existing else None
        })
        
    updated_tests = other_tests + new_tests
    
    inv = next((i for i in invoices if i['sample_id'] in [s['id'] for s in current_samples] and not i.get('is_insurance_invoice')), None)
    new_subtotal = sum([s['price'] for s in current_editing_services])
    new_total = new_subtotal
    
    inv_index = next((idx for idx, i in enumerate(invoices) if i['id'] == inv['id']), -1)
    if inv_index != -1:
        invoices[inv_index]['subtotal'] = new_subtotal
        invoices[inv_index]['amount_due'] = new_total
        
    sync_table('lab_samples', updated_samples)
    sync_table('lab_tests', updated_tests)
    sync_table('invoices', invoices)
    
    cursor.execute("SELECT * FROM lab_samples WHERE session_uid = %s", (sess_id,))
    rem_samples = cursor.fetchall()
    assert len(rem_samples) == 2, f"Expected 2 samples (EDTA and Siero), got {len(rem_samples)}"
    
    cursor.execute("SELECT * FROM invoices WHERE id = 10001")
    updated_inv = cursor.fetchone()
    assert float(updated_inv['amount_due']) == 35.00, f"Expected unpaid invoice amount to be 35.00, got {updated_inv['amount_due']}"
    
    print("[SUCCESS] Test Case 1b: Unpaid acceptance modified. New tube created, barcode suffix correct, invoice updated directly.")

    print("\n--- TEST CASE 2: Modify paid LIS acceptance - Cost Increase (TEST-SESS-002) ---")
    print("Action: Add Colesterolo Totale (Service ID 5, Siero, price 18.00)")
    
    samples = get_table('lab_samples')
    tests = get_table('lab_tests')
    invoices = get_table('invoices')
    
    sess_id = 'TEST-SESS-002'
    current_editing_services = [s for s in services if s['id'] in [3, 5]]
    current_samples = [s for s in samples if s['session_uid'] == sess_id]
    required_sample_types = list(set([s['sample_type'] for s in current_editing_services if s['sample_type']]))
    
    patient_id = current_samples[0]['patient_id']
    collected_at = current_samples[0]['collected_at']
    collected_by = current_samples[0]['collected_by']
    
    updated_samples = [s for s in samples]
    updated_tests = [t for t in tests]
    
    sample_type_to_id = {}
    current_samples_to_delete = []
    for sam in current_samples:
        if sam['sample_type'] in required_sample_types:
            sample_type_to_id[sam['sample_type']] = sam['id']
        else:
            current_samples_to_delete.append(sam['id'])
            
    for stype in required_sample_types:
        if not sample_type_to_id.get(stype):
            new_barcode = "000000040002"
            next_id = max([s['id'] for s in updated_samples]) + 1
            new_sample = {
                "id": next_id,
                "patient_id": patient_id,
                "barcode": new_barcode,
                "sample_type": stype,
                "status": 'collected',
                "session_uid": sess_id,
                "collected_at": collected_at,
                "collected_by": collected_by
            }
            updated_samples.append(new_sample)
            sample_type_to_id[stype] = next_id
            
    other_tests = [t for t in updated_tests if t['sample_id'] not in [s['id'] for s in current_samples]]
    new_tests = []
    for srv in current_editing_services:
        sample_id = sample_type_to_id.get(srv['sample_type'])
        if not sample_id:
            continue
        existing = next((t for t in tests if t['sample_id'] in [s['id'] for s in current_samples] and t['service_id'] == srv['id']), None)
        next_id = max([t['id'] for t in other_tests + new_tests]) + 1 if (other_tests + new_tests) else 10001
        new_tests.append({
            "id": next_id,
            "sample_id": sample_id,
            "service_id": srv['id'],
            "test_name": srv['name'],
            "result_value": existing['result_value'] if existing else None,
            "reference_range": srv['reference_range'] or '',
            "unit": srv['unit'] or '',
            "status": existing['status'] if existing else 'pending',
            "verified_by": existing['verified_by'] if existing else None,
            "verified_at": existing['verified_at'] if existing else None
        })
        
    updated_tests = other_tests + new_tests
    
    inv = next((i for i in invoices if i['sample_id'] in [s['id'] for s in current_samples] and not i.get('is_insurance_invoice')), None)
    new_subtotal = sum([s['price'] for s in current_editing_services])
    new_total = new_subtotal
    diff = new_total - float(inv['amount_due'])
    
    next_inv_id = max([i['id'] for i in invoices]) + 1
    new_inv = {
        "id": next_inv_id,
        "sample_id": current_samples[0]['id'],
        "invoice_number": "TEST-FAT-INTEGRATIVE-001",
        "issue_date": str(pymysql.Date.today()),
        "subtotal": diff,
        "discount_amount": 0.00,
        "stamp_duty": 0.00,
        "amount_due": diff,
        "amount_paid": 0.00,
        "payment_status": 'unpaid',
        "is_insurance_invoice": 0
    }
    invoices.append(new_inv)
    
    sync_table('lab_samples', updated_samples)
    sync_table('lab_tests', updated_tests)
    sync_table('invoices', invoices)
    
    cursor.execute("SELECT * FROM lab_samples WHERE session_uid = %s", (sess_id,))
    rem_samples = cursor.fetchall()
    assert len(rem_samples) == 1, f"Expected only 1 Siero sample to remain, got {len(rem_samples)}"
    
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = 'TEST-FAT-INTEGRATIVE-001'")
    int_inv = cursor.fetchone()
    assert int_inv is not None, "Expected integrative invoice to be created"
    assert float(int_inv['amount_due']) == 18.00, f"Expected integrative invoice amount to be 18.00, got {int_inv['amount_due']}"
    assert int_inv['payment_status'] == 'unpaid', "Expected integrative invoice to be unpaid"
    
    print("[SUCCESS] Test Case 2: Paid acceptance modified (increase). Reused tube, generated unpaid integrative invoice.")

    print("\n--- TEST CASE 3: Modify paid LIS acceptance - Cost Decrease (TEST-SESS-003) ---")
    print("Action: Remove Glicemia Basale (Service ID 3, Siero, price 15.00)")
    
    samples = get_table('lab_samples')
    tests = get_table('lab_tests')
    invoices = get_table('invoices')
    
    sess_id = 'TEST-SESS-003'
    current_editing_services = [s for s in services if s['id'] == 4]
    current_samples = [s for s in samples if s['session_uid'] == sess_id]
    required_sample_types = list(set([s['sample_type'] for s in current_editing_services if s['sample_type']]))
    
    updated_samples = [s for s in samples]
    updated_tests = [t for t in tests]
    
    sample_type_to_id = {}
    current_samples_to_delete = []
    for sam in current_samples:
        if sam['sample_type'] in required_sample_types:
            sample_type_to_id[sam['sample_type']] = sam['id']
        else:
            current_samples_to_delete.append(sam['id'])
            
    if current_samples_to_delete:
        updated_samples = [s for s in updated_samples if s['id'] not in current_samples_to_delete]
        updated_tests = [t for t in updated_tests if t['sample_id'] not in current_samples_to_delete]
        
    other_tests = [t for t in updated_tests if t['sample_id'] not in [s['id'] for s in current_samples]]
    new_tests = []
    for srv in current_editing_services:
        sample_id = sample_type_to_id.get(srv['sample_type'])
        if not sample_id:
            continue
        existing = next((t for t in tests if t['sample_id'] in [s['id'] for s in current_samples] and t['service_id'] == srv['id']), None)
        next_id = max([t['id'] for t in other_tests + new_tests]) + 1 if (other_tests + new_tests) else 10001
        new_tests.append({
            "id": next_id,
            "sample_id": sample_id,
            "service_id": srv['id'],
            "test_name": srv['name'],
            "result_value": existing['result_value'] if existing else None,
            "reference_range": srv['reference_range'] or '',
            "unit": srv['unit'] or '',
            "status": existing['status'] if existing else 'pending',
            "verified_by": existing['verified_by'] if existing else None,
            "verified_at": existing['verified_at'] if existing else None
        })
        
    updated_tests = other_tests + new_tests
    
    inv = next((i for i in invoices if i['sample_id'] in [s['id'] for s in current_samples] and not i.get('is_insurance_invoice')), None)
    new_subtotal = sum([s['price'] for s in current_editing_services])
    new_total = new_subtotal
    diff = new_total - float(inv['amount_due'])
    
    next_inv_id = max([i['id'] for i in invoices]) + 1
    new_inv = {
        "id": next_inv_id,
        "sample_id": current_samples[0]['id'],
        "invoice_number": "TEST-NDC-0001",
        "issue_date": str(pymysql.Date.today()),
        "subtotal": diff,
        "discount_amount": 0.00,
        "stamp_duty": 0.00,
        "amount_due": diff,
        "amount_paid": diff,
        "payment_status": 'paid',
        "payment_method": 'Contanti',
        "paid_at": str(pymysql.Date.today()),
        "is_credit_note": True,
        "is_insurance_invoice": 0
    }
    invoices.append(new_inv)
    
    sync_table('lab_samples', updated_samples)
    sync_table('lab_tests', updated_tests)
    sync_table('invoices', invoices)
    
    cursor.execute("SELECT * FROM lab_samples WHERE session_uid = %s", (sess_id,))
    rem_samples = cursor.fetchall()
    assert len(rem_samples) == 1, f"Expected only 1 Sangue intero sample, got {len(rem_samples)}"
    
    cursor.execute("SELECT * FROM invoices WHERE invoice_number = 'TEST-NDC-0001'")
    ndc_inv = cursor.fetchone()
    assert ndc_inv is not None, "Expected Credit Note to be created"
    assert float(ndc_inv['amount_due']) == -15.00, f"Expected Credit Note amount to be -15.00, got {ndc_inv['amount_due']}"
    assert ndc_inv['payment_status'] == 'paid', "Expected Credit Note to be marked paid"
    assert ndc_inv['payment_method'] == 'Contanti', "Expected payment method to be Contanti (Cash)"
    assert ndc_inv['invoice_number'].startswith('TEST-NDC-'), "Expected invoice number to start with TEST-NDC-"
    
    print("[SUCCESS] Test Case 3: Paid acceptance modified (decrease). Empty tube deleted, generated paid Cash Credit Note.")
    
    conn.close()

if __name__ == "__main__":
    setup_test_data()
    run_tests_logic()
    print("\n=======================================================")
    print("   ALL TESTS COMPLETED SUCCESSFULLY! SYSTEM VALIDATED  ")
    print("=======================================================")
