import json
import pymysql

with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

conn = pymysql.connect(
    host=config.get('db_host', 'localhost'),
    port=int(config.get('db_port', 3306)),
    user=config.get('db_user', 'root'),
    password=config.get('db_pass', ''),
    database=config.get('db_name', 'nextcare_db'),
    charset='utf8mb4'
)

# Ensure patients 1, 2, and 3 exist to prevent foreign key errors
with conn.cursor() as cursor:
    for pid in [1, 2, 3]:
        cursor.execute("SELECT id FROM patients WHERE id = %s", (pid,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO patients (id, first_name, last_name, tax_code, gender, birth_date, email, phone) 
                VALUES (%s, 'Paziente', %s, CONCAT('TAXCODE00', %s), 'M', '1990-01-01', 'p@example.com', '333')
            """, (pid, str(pid), str(pid)))
    conn.commit()

samples = [
    (30, 1, "MICROBAR001", "Urine (Contenitore Standard)", "completed", "SESS-MICRO-001", "2026-06-14 08:00:00", 4),
    (31, 2, "MICROBAR002", "Tampone sterile", "completed", "SESS-MICRO-002", "2026-06-14 08:30:00", 4),
    (32, 3, "MICROBAR003", "Feci (Contenitore idoneo)", "completed", "SESS-MICRO-003", "2026-06-14 09:00:00", 4),
    (33, 1, "MICROBAR004", "Urine (Contenitore Standard)", "collected", "SESS-MICRO-004", "2026-06-14 18:00:00", 4),
    (34, 2, "MICROBAR005", "Tampone sterile", "collected", "SESS-MICRO-005", "2026-06-14 18:15:00", 4)
]

tests = [
    (50, 30, 101, "Urinocoltura da coltura (LIS)", "Sterile", "Sterile", "completed", 8, "2026-06-14 12:00:00"),
    (51, 31, 102, "Tampone Faringeo per Streptococco (LIS)", "Sviluppo Batterico", "Negativo", "completed", 8, "2026-06-14 12:15:00"),
    (52, 32, 103, "Coprocoltura (LIS)", "Sviluppo Batterico", "Negativo per batteri patogeni", "completed", 8, "2026-06-14 12:30:00"),
    (53, 33, 101, "Urinocoltura da coltura (LIS)", None, "Sterile", "pending", None, None),
    (54, 34, 102, "Tampone Faringeo per Streptococco (LIS)", None, "Negativo", "pending", None, None)
]

results = [
    (1, 50, 1, "Esame colturale negativo per batteri aerobi dopo 48 ore di incubazione.", None, None, None, None, None, None),
    (2, 51, 0, "Isolato sviluppo di Streptococcus pyogenes (Gruppo A).", 8, 
     json.dumps([
         {"antibiotic_id": 2, "susceptibility": "S", "mic": "<= 0.25"},
         {"antibiotic_id": 5, "susceptibility": "R", "mic": ">= 8"},
         {"antibiotic_id": 49, "susceptibility": "S", "mic": "<= 0.5"}
     ]), None, None, None, None),
    (3, 52, 0, "Isolati ceppi di Escherichia coli e Salmonella enteritidis.", 40,
     json.dumps([
         {"antibiotic_id": 3, "susceptibility": "S", "mic": "<= 4"},
         {"antibiotic_id": 39, "susceptibility": "S", "mic": "<= 0.12"},
         {"antibiotic_id": 54, "susceptibility": "I", "mic": "4"}
     ]), 56,
     json.dumps([
         {"antibiotic_id": 4, "susceptibility": "R", "mic": ">= 32"},
         {"antibiotic_id": 39, "susceptibility": "S", "mic": "<= 0.06"}
     ]), None, None)
]

try:
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        
        # Delete old seeded keys if they exist
        cursor.execute("DELETE FROM `lab_samples` WHERE id IN (30, 31, 32, 33, 34)")
        cursor.execute("DELETE FROM `lab_tests` WHERE id IN (50, 51, 52, 53, 54)")
        cursor.execute("DELETE FROM `lis_microbiology_results` WHERE id IN (1, 2, 3)")
        
        # Insert samples
        for s in samples:
            cursor.execute("""
                INSERT INTO `lab_samples` (id, patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, s)
            
        # Insert tests
        for t in tests:
            cursor.execute("""
                INSERT INTO `lab_tests` (id, sample_id, service_id, test_name, result_value, reference_range, status, verified_by, verified_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, t)
            
        # Insert microbiology results
        for r in results:
            cursor.execute("""
                INSERT INTO `lis_microbiology_results` (id, test_id, is_negative, notes, germ1_id, germ1_antibiotics, germ2_id, germ2_antibiotics, germ3_id, germ3_antibiotics)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, r)
            
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        print("Successfully seeded microbiology cases with pending tests.")
    conn.commit()
finally:
    conn.close()
