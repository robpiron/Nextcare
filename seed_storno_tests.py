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

def seed():
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # 0. Clean up old test data
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM lab_tests WHERE id >= 10000")
    cursor.execute("DELETE FROM lab_samples WHERE id >= 10000")
    cursor.execute("DELETE FROM radiology_studies WHERE id >= 10000")
    cursor.execute("DELETE FROM invoices WHERE id >= 10000")
    cursor.execute("DELETE FROM patients WHERE id = 10")
    
    # 1. Insert patient
    cursor.execute("""
        INSERT INTO patients (id, uuid, tax_code, first_name, last_name, birth_date, gender, email, phone, address)
        VALUES (10, '550e8400-e29b-41d4-a716-446655449999', 'TSTRSS80A01H501T', 'Test Storno', 'Rossi', '1980-01-01', 'M', 'test.storno@nextcare.it', '+39 333 1122333', 'Via Milano 1, Milano')
    """)
    
    # ==========================================
    # CASO 1: Accettazione LIS NON Pagata (Modifica Importo Diretta)
    # Esami: Emocromo (20.00) + Glicemia (15.00) = 35.00 unpaid
    # ==========================================
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10001, 10, 'TSTBAR001001', 'Sangue intero (EDTA - Viola)', 'collected', 'SESS-TEST-STORNO-UNPAID', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10002, 10, 'TSTBAR001002', 'Siero (Attivatore - Rosso)', 'collected', 'SESS-TEST-STORNO-UNPAID', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10001, 10001, 4, 'Emocromo Completo (LIS)', NULL, '4.5-5.9', '10^6/uL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10002, 10002, 3, 'Glicemia Basale (LIS)', NULL, '70-100', 'mg/dL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO invoices (id, sample_id, invoice_number, issue_date, subtotal, discount_amount, stamp_duty, amount_due, amount_paid, payment_status, is_insurance_invoice)
        VALUES (10001, 10001, 'FAT-TEST-UNPAID', CURDATE(), 35.00, 0.00, 0.00, 35.00, 0.00, 'unpaid', 0)
    """)
    
    # ==========================================
    # CASO 2: Accettazione LIS Pagata (Emissione Nota di Credito)
    # Esami: Emocromo (20.00) + Glicemia (15.00) = 35.00 paid
    # ==========================================
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10003, 10, 'TSTBAR002001', 'Sangue intero (EDTA - Viola)', 'collected', 'SESS-TEST-STORNO-PAID-NC', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10004, 10, 'TSTBAR002002', 'Siero (Attivatore - Rosso)', 'collected', 'SESS-TEST-STORNO-PAID-NC', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10003, 10003, 4, 'Emocromo Completo (LIS)', NULL, '4.5-5.9', '10^6/uL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10004, 10004, 3, 'Glicemia Basale (LIS)', NULL, '70-100', 'mg/dL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO invoices (id, sample_id, invoice_number, issue_date, subtotal, discount_amount, stamp_duty, amount_due, amount_paid, payment_status, payment_method, paid_at, is_insurance_invoice)
        VALUES (10002, 10003, 'FAT-TEST-PAID-NC', CURDATE(), 35.00, 0.00, 0.00, 35.00, 35.00, 'paid', 'Carta di Credito', NOW(), 0)
    """)
    
    # ==========================================
    # CASO 3: Accettazione LIS Pagata (Emissione Fattura Integrativa)
    # Esami: Glicemia (15.00) = 15.00 paid
    # ==========================================
    cursor.execute("""
        INSERT INTO lab_samples (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
        VALUES (10005, 10, 'TSTBAR003002', 'Siero (Attivatore - Rosso)', 'collected', 'SESS-TEST-STORNO-PAID-INT', NOW(), 4)
    """)
    cursor.execute("""
        INSERT INTO lab_tests (id, sample_id, service_id, test_name, result_value, reference_range, unit, status)
        VALUES (10005, 10005, 3, 'Glicemia Basale (LIS)', NULL, '70-100', 'mg/dL', 'pending')
    """)
    cursor.execute("""
        INSERT INTO invoices (id, sample_id, invoice_number, issue_date, subtotal, discount_amount, stamp_duty, amount_due, amount_paid, payment_status, payment_method, paid_at, is_insurance_invoice)
        VALUES (10003, 10005, 'FAT-TEST-PAID-INT', CURDATE(), 15.00, 0.00, 0.00, 15.00, 15.00, 'paid', 'Carta di Credito', NOW(), 0)
    """)
    
    # ==========================================
    # CASO 4: Accettazione RIS Modificabile (Scheduled)
    # Esame: Radiografia standard RX Torace (120.00)
    # ==========================================
    cursor.execute("""
        INSERT INTO radiology_studies (id, patient_id, doctor_id, service_id, study_type, scheduled_at, status, dicom_series_uid)
        VALUES (10001, 10, 1, 6, 'XRAY', DATE_ADD(NOW(), INTERVAL 1 DAY), 'scheduled', '1.2.840.113619.2.134.10001')
    """)
    cursor.execute("""
        INSERT INTO invoices (id, study_id, invoice_number, issue_date, subtotal, discount_amount, stamp_duty, amount_due, amount_paid, payment_status, payment_method, paid_at, is_insurance_invoice)
        VALUES (10004, 10001, 'FAT-TEST-RIS-PAID', CURDATE(), 120.00, 0.00, 0.00, 120.00, 120.00, 'paid', 'Bancomat', NOW(), 0)
    """)
    
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    print("\n[SUCCESS] Casi di test per storni e note di credito inseriti con successo nel database MySQL!")
    print("Dettagli Paziente Creato:")
    print("  - Nome: Test Storno Rossi")
    print("  - Codice Fiscale: TSTRSS80A01H501T")
    print("\nAccettazioni disponibili:")
    print("  1. LIS NON Pagata (SESS-TEST-STORNO-UNPAID) -> Importo 35.00€ (Emocromo + Glicemia)")
    print("  2. LIS Pagata (SESS-TEST-STORNO-PAID-NC)     -> Importo 35.00€ (Emocromo + Glicemia)")
    print("  3. LIS Pagata (SESS-TEST-STORNO-PAID-INT)    -> Importo 15.00€ (Glicemia)")
    print("  4. RIS Pagata (Radiografia scheduled)        -> Importo 120.00€ (RX Torace)")
    conn.close()

if __name__ == "__main__":
    seed()
