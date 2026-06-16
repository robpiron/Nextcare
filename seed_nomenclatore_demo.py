import os
import re
import json
import uuid
import datetime
import random
import pandas as pd
import pymysql

# 1. Load DB connection config
config_path = "config.json"
if not os.path.exists(config_path):
    raise FileNotFoundError("config.json not found in the current folder.")

with open(config_path, "r", encoding="utf-8") as f:
    config = json.load(f)

db_host = config.get("db_host", "localhost")
db_port = int(config.get("db_port", 3306))
db_user = config.get("db_user", "root")
db_pass = config.get("db_pass", "")
db_name = config.get("db_name", "nextcare_db")

excel_path = "C:\\Users\\robpiron\\.gemini\\antigravity\\scratch\\nomenclatore.xlsx"
if not os.path.exists(excel_path):
    raise FileNotFoundError(f"Excel file not found at: {excel_path}")

print(f"Connecting to MySQL database {db_name} on {db_host}:{db_port}...")
conn = pymysql.connect(
    host=db_host,
    port=db_port,
    user=db_user,
    password=db_pass,
    database=db_name,
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor
)
cursor = conn.cursor()

# 2. Refined Guessers
def guess_dose_class_id(name):
    if not name:
        return None
    lower = name.lower().strip()
    
    # Class 0: Ecografia, Risonanza
    if 'ecografia' in lower or 'risonanza' in lower or ' eco ' in lower or lower.startswith('eco ') or 'ecocolordoppler' in lower or 'ecocardiografia' in lower or 'ecostress' in lower or 'ecocardio' in lower or re.search(r'\brm\b', lower) or re.search(r'\brmn\b', lower):
        return 1
        
    # Class IV: Interventistica, Angiografia, coronarografia, angioTC, total body, TC addome completo/totale
    if 'interventistica' in lower or 'angiografia' in lower or 'coronarografia' in lower or 'angiotc' in lower or 'angio-tc' in lower or 'total body' in lower or 'completo' in lower or 'completa' in lower or 'totale' in lower:
        return 5
        
    # Class III / II for CT/TC
    if 'tc' in lower or 'ct' in lower or 'tac' in lower:
        if 'cranio' in lower or 'encefalo' in lower or 'testa' in lower or 'orbite' in lower or 'rocche' in lower or 'sella' in lower:
            return 3 # Class II
        return 4 # Class III
        
    # Class II: RX Addome, RX Digerente
    if ('radiografia' in lower or 'radiografico' in lower or re.search(r'\brx\b', lower)) and ('addome' in lower or 'digerente' in lower or 'clisma' in lower or 'uretrografia' in lower):
        return 3 # Class II
        
    # Class I: Basic X-Ray
    if 'radiografia' in lower or 'radiografico' in lower or 'ortopantomografia' in lower or 'telecuore' in lower or 'mammografia' in lower or 'mammografico' in lower or re.search(r'\brx\b', lower) or re.search(r'\bopt\b', lower):
        return 2 # Class I
        
    return None

def guess_lis_fields(name):
    lower = name.lower()
    if 'tampone' in lower or 'coltura' in lower or 'colturale' in lower or 'microb' in lower:
        return 2, "Tampone (Fissativo)" # 2 = Tampone Microbiologico
    elif 'urina' in lower or 'urine' in lower or 'urinario' in lower:
        return 3, "Contenitore Urine (Giallo)" # 3 = Raccolta Urine
    elif 'arterioso' in lower or 'emogas' in lower:
        return 4, "Sangue Arterioso" # 4 = Prelievo Arterioso
    else:
        return 1, "Siero (Attivatore - Rosso)" # 1 = Prelievo Venoso

# 3. Truncate existing tables to start with a clean slate
print("Wiping existing transactional and medical services tables...")
tables_to_wipe = [
    "patient_consents", "patient_claims", "sent_emails", "lab_tests", "lab_samples", 
    "lab_reports", "radiology_studies", "invoices", "prima_nota_movements", "admissions", 
    "appointment_services", "appointments", "doctor_agenda_services", "price_list_items", 
    "medical_services", "patients"
]

cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
for t in tables_to_wipe:
    cursor.execute(f"TRUNCATE TABLE `{t}`")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
conn.commit()
print("Tables wiped and auto-increment indexes reset to 1.")

# Ensure biologist staff member Chiara Lanza (ID 8) exists
cursor.execute("SELECT id FROM staff WHERE id = 8")
if not cursor.fetchone():
    print("Seeding biologist Chiara Lanza (ID 8)...")
    cursor.execute("""
        INSERT INTO staff (id, first_name, last_name, role, email, phone, active, username, password, profiles)
        VALUES (8, 'Chiara', 'Lanza', 'technician', 'c.lanza@nextcare.it', '+39 333 8888888', 1, 'lanza', 'Password123', '["biologo"]')
    """)
    conn.commit()


# 4. Parse nomenclatore.xlsx
print(f"Reading Excel nomenclator from: {excel_path}...")
df = pd.read_excel(excel_path)
df.columns = [str(c).strip() for c in df.columns]

print(f"Found {len(df)} rows in Excel nomenclator. Beginning import into database...")

imported_services = []
services_by_type = {"lis": [], "ris": [], "visita": []}

for idx, row in df.iterrows():
    # Positional access to be safe: Col 2 (C) is Code, Col 3 (D) is Descrizione, Col 6 (G) is Tariffa, Col 7 (H) is Branca 1
    code = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else None
    name = str(row.iloc[3]).strip() if pd.notna(row.iloc[3]) else None
    price_val = row.iloc[6]
    price = float(price_val) if pd.notna(price_val) else 0.0
    branch = str(row.iloc[7]).strip() if pd.notna(row.iloc[7]) else "Generale"
    
    if not code or not name:
        continue
        
    branch_lower = branch.lower()
    
    # Classify type
    if branch_lower in ["laboratorio", "laboratorio"]:
        srv_type = "lis"
        profit_center = "LABORATORIO"
        clinic_id = 3 # Laboratorio Analisi Cliniche
        equipment_id = None
        instrument_id = random.choice([10, 11, 12])
        sc_type_id, sample_type = guess_lis_fields(name)
        dose_class_id = None
        parameters = json.dumps([{"name": name, "unit": "mg/dL", "reference_range": "70-100"}])
    elif branch_lower == "diagnostica per immagini":
        srv_type = "ris"
        profit_center = "IMAGING"
        clinic_id = 2 # Sala Diagnostica RX
        sc_type_id = None
        sample_type = None
        parameters = None
        dose_class_id = guess_dose_class_id(name)
        instrument_id = None
        # 1 for RX Siemens, 2 for MRI GE
        if 'risonanza' in name.lower() or 'rmn' in name.lower() or 'rm' in name.lower():
            equipment_id = 2
        else:
            equipment_id = 1
    else:
        srv_type = "visita"
        profit_center = "SPECIALISTICA"
        clinic_id = 1 # Ambulatorio Medici
        sc_type_id = None
        sample_type = None
        parameters = None
        dose_class_id = None
        equipment_id = None
        instrument_id = None

    # Alert note default
    alert_note = None
    if srv_type == "lis" and sc_type_id == 1:
        alert_note = "Consigliato digiuno di 8 ore prima del prelievo."
    elif srv_type == "ris" and equipment_id == 1:
        alert_note = "Rimuovere oggetti metallici o gioielli dal torace/arti prima dell'esame."
    elif srv_type == "ris" and equipment_id == 2:
        alert_note = "Obbligatorio segnalare presenza di pacemaker o corpi ferromagnetici."

    imported_services.append((
        name, srv_type, code, branch, price, clinic_id, equipment_id, 
        sample_type, sc_type_id, parameters, alert_note, profit_center, dose_class_id, instrument_id
    ))

# 5. Bulk insert services into medical_services
sql_insert_service = """
    INSERT INTO medical_services (
        name, type, code, branch, price, clinic_id, equipment_id, 
        sample_type, sample_collection_type_id, parameters, alert_note, profit_center, dose_class_id, instrument_id
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

print(f"Executing bulk insert for {len(imported_services)} medical services...")
cursor.executemany(sql_insert_service, imported_services)
conn.commit()

# Fetch inserted services to group them
cursor.execute("SELECT id, name, type, code, branch, price, sample_type, reference_range, unit FROM medical_services")
db_services = cursor.fetchall()
for ds in db_services:
    services_by_type[ds["type"]].append(ds)

print(f"Successfully imported nomenclator services:")
print(f"  - LIS services: {len(services_by_type['lis'])}")
print(f"  - RIS services: {len(services_by_type['ris'])}")
print(f"  - Visite/Specialistica services: {len(services_by_type['visita'])}")

# 6. Recreate some composite packages
print("Creating check-up and promo packages...")
package_base = {
    "name": "Pacchetto Check-up Base LIS",
    "type": "pacchetto",
    "code": "PKG-001",
    "branch": "Laboratorio",
    "price": 35.00,
    "profit_center": "LABORATORIO",
    "alert_note": "Include Emocromo e Glicemia. Digiuno consigliato."
}
lis_sample_services = services_by_type["lis"][:3]
lis_sample_ids = [s["id"] for s in lis_sample_services]
cursor.execute("""
    INSERT INTO medical_services (name, type, code, branch, price, profit_center, alert_note, package_items)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (
    package_base["name"], package_base["type"], package_base["code"], package_base["branch"], 
    package_base["price"], package_base["profit_center"], package_base["alert_note"], json.dumps(lis_sample_ids)
))

package_cardio = {
    "name": "Pacchetto Screening Cardio-Polmonare",
    "type": "pacchetto",
    "code": "PKG-002",
    "branch": "Diagnostica Integrata",
    "price": 140.00,
    "profit_center": "SPECIALISTICA",
    "alert_note": "Comprende Visita Cardiologica e Radiografia RX Torace."
}
cardio_services = [s for s in services_by_type["visita"] if "cardio" in s["name"].lower()][:1]
torace_services = [s for s in services_by_type["ris"] if "torace" in s["name"].lower()][:1]
if not cardio_services:
    cardio_services = services_by_type["visita"][:1]
if not torace_services:
    torace_services = services_by_type["ris"][:1]

cardio_promo_ids = [s["id"] for s in (cardio_services + torace_services)]
cursor.execute("""
    INSERT INTO medical_services (name, type, code, branch, price, profit_center, alert_note, package_items)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
""", (
    package_cardio["name"], package_cardio["type"], package_cardio["code"], package_cardio["branch"], 
    package_cardio["price"], package_cardio["profit_center"], package_cardio["alert_note"], json.dumps(cardio_promo_ids)
))
conn.commit()

# 7. Associate new services with doctor agendas in doctor_agenda_services
print("Associating services with doctor agendas...")
agenda_service_inserts = []

for s in db_services:
    if s["type"] == "ris":
        agenda_service_inserts.append((2, s["id"])) # doctor 2
    elif s["type"] == "visita":
        if "cardio" in s["name"].lower() or "visita" in s["name"].lower():
            agenda_service_inserts.append((1, s["id"])) # doctor 1
        elif "chirurg" in s["name"].lower():
            agenda_service_inserts.append((3, s["id"])) # doctor 3
        else:
            agenda_service_inserts.append((1, s["id"])) # doctor 1 (fallback)

cursor.executemany("INSERT INTO doctor_agenda_services (agenda_id, service_id) VALUES (%s, %s)", agenda_service_inserts)
conn.commit()
print(f"Associated {len(agenda_service_inserts)} services with doctor agendas.")

# 8. Generate 50 Patients
print("Generating 50 realistic patient records...")
m_names = ["Mario", "Luigi", "Giovanni", "Francesco", "Alessandro", "Roberto", "Luca", "Marco", "Giuseppe", "Antonio", "Stefano", "Andrea", "Davide", "Federico", "Lorenzo", "Simone", "Matteo", "Filippo", "Gabriele", "Enrico"]
f_names = ["Maria", "Francesca", "Anna", "Giulia", "Sofia", "Elena", "Chiara", "Laura", "Sara", "Alessia", "Silvia", "Federica", "Giorgia", "Valentina", "Martina", "Alice", "Elisa", "Beatrice", "Camilla", "Emma"]
surnames = ["Rossi", "Ferrari", "Russo", "Bianchi", "Romano", "Colombo", "Marino", "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Costa", "Giordano", "Mancini", "Rizzo", "Lombardi", "Moretti", "Barbieri", "Fontana", "Ricci", "Santoro", "Piras", "Leone", "Longhi"]

patients_data = []

def generate_cf(first_name, last_name, birth_date, gender):
    l_consonants = "".join([c for c in last_name.upper() if c not in "AEIOU "])
    f_consonants = "".join([c for c in first_name.upper() if c not in "AEIOU "])
    l_part = (l_consonants + "XXX")[:3]
    f_part = (f_consonants + "XXX")[:3]
    yy = f"{birth_date.year:04d}"[2:]
    months = ['A', 'B', 'C', 'D', 'E', 'H', 'L', 'M', 'P', 'R', 'S', 'T']
    mm = months[birth_date.month - 1]
    day = birth_date.day
    if gender == 'F':
        day += 40
    dd = f"{day:02d}"
    town = "H501" # Rome
    ctrl = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    return f"{l_part}{f_part}{yy}{mm}{dd}{town}{ctrl}"

random.seed(42) # Seed for reproducibility

for i in range(1, 51):
    gender = random.choice(['M', 'F'])
    first_name = random.choice(m_names) if gender == 'M' else random.choice(f_names)
    last_name = random.choice(surnames)
    
    # Random birthday between 1945 and 2012
    birth_year = random.randint(1945, 2012)
    birth_month = random.randint(1, 12)
    birth_day = random.randint(1, 28)
    bdate = datetime.date(birth_year, birth_month, birth_day)
    
    cf = generate_cf(first_name, last_name, bdate, gender)
    # Ensure uniqueness of CF
    while any(p[1] == cf for p in patients_data):
        cf = generate_cf(first_name, last_name, bdate, gender)
        
    p_uuid = str(uuid.uuid4())
    email = f"{first_name.lower()}.{last_name.lower()}{i}@example.com"
    phone = f"+39 3{random.randint(10, 99):02d} {random.randint(1000000, 9999999)}"
    address = f"Via Roma {random.randint(1, 250)}, Roma"
    
    patients_data.append((p_uuid, cf, first_name, last_name, bdate, gender, email, phone, address))

sql_patient_insert = """
    INSERT INTO patients (uuid, tax_code, first_name, last_name, birth_date, gender, email, phone, address)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
"""
cursor.executemany(sql_patient_insert, patients_data)
conn.commit()

# Retrieve patient IDs
cursor.execute("SELECT id, tax_code, first_name, last_name FROM patients")
db_patients = cursor.fetchall()
print(f"Seeded {len(db_patients)} patients in MySQL database.")

# 9. Create CUP Bookings (Appointments)
# - 10 active bookings (future dates, status 'scheduled')
# - 15 past bookings (past dates, status 'completed')
# - 12 no-show bookings (past dates, status 'no_show')
print("Seeding CUP appointments...")
appointment_records = []
today = datetime.datetime.now()

# Helper to generate random time
def rand_time():
    hour = random.choice([8, 9, 10, 11, 12, 14, 15, 16, 17, 18])
    minute = random.choice([0, 15, 30, 45])
    return hour, minute

# 10 Active
for i in range(10):
    p = db_patients[i]
    if i < 4:
        days_in_future = 0
    else:
        days_in_future = random.randint(1, 14)
    h, m = rand_time()
    dt = today.replace(hour=h, minute=m, second=0, microsecond=0) + datetime.timedelta(days=days_in_future)
    doc_id = random.choice([1, 2, 3])
    appointment_records.append((p["id"], doc_id, dt, 'scheduled', 'Prenotazione attiva dal CUP.'))

# 15 Past Completed
for i in range(15):
    p = db_patients[10 + i]
    days_in_past = random.randint(2, 14)
    h, m = rand_time()
    dt = today.replace(hour=h, minute=m, second=0, microsecond=0) - datetime.timedelta(days=days_in_past)
    doc_id = random.choice([1, 2, 3])
    appointment_records.append((p["id"], doc_id, dt, 'completed', 'Prenotazione passata completata.'))

# 12 No-Show
for i in range(12):
    p = db_patients[25 + i]
    days_in_past = random.randint(2, 14)
    h, m = rand_time()
    dt = today.replace(hour=h, minute=m, second=0, microsecond=0) - datetime.timedelta(days=days_in_past)
    doc_id = random.choice([1, 2, 3])
    appointment_records.append((p["id"], doc_id, dt, 'no_show', 'Paziente non presentatosi (No-Show).'))

sql_insert_app = """
    INSERT INTO appointments (patient_id, doctor_id, appointment_datetime, status, notes)
    VALUES (%s, %s, %s, %s, %s)
"""
for app in appointment_records:
    cursor.execute(sql_insert_app, app)
conn.commit()

# Link services to appointments
cursor.execute("SELECT id, doctor_id FROM appointments")
db_appointments = cursor.fetchall()
app_services_inserts = []
for app in db_appointments:
    doc_id = app["doctor_id"]
    doc_services = [s for s in db_services if s["type"] == ("ris" if doc_id == 2 else "visita")]
    if doc_services:
        srv = random.choice(doc_services)
        app_services_inserts.append((app["id"], srv["id"]))

cursor.executemany("INSERT INTO appointment_services (appointment_id, service_id) VALUES (%s, %s)", app_services_inserts)
conn.commit()
print(f"Seeded {len(db_appointments)} appointments with associated services.")

# 10. Generate 23 RIS Acceptances
# - 1 "aperta da fatturare": status 'scheduled', invoice unpaid
# - 7 "da erogare": status 'scheduled', invoice paid
# - 7 "da refertare": status 'executed', invoice paid, report_text = NULL
# - 8 "già refertate": status 'completed', invoice paid, report_text & signature filled
print("Seeding 23 RIS radiology acceptances...")
ris_patient_pool = db_patients[:23]
ris_services_pool = services_by_type["ris"]

if not ris_services_pool:
    print("WARNING: No RIS services found to seed radiology studies!")
else:
    invoice_count = 1
    
    for idx, patient in enumerate(ris_patient_pool):
        if idx == 0:
            status = 'scheduled'
            inv_status = 'unpaid'
            report_text = None
            signed_by = None
            signed_at = None
            adm_status = 'active'
        elif idx <= 7:
            status = 'scheduled'
            inv_status = 'paid'
            report_text = None
            signed_by = None
            signed_at = None
            adm_status = 'active'
        elif idx <= 14:
            status = 'executed'
            inv_status = 'paid'
            report_text = None
            signed_by = None
            signed_at = None
            adm_status = 'active'
        else:
            status = 'completed'
            inv_status = 'paid'
            report_text = "Si osserva regolare trasparenza dei campi polmonari, ombra cardio-mediastinica nei limiti. Non versamenti pleurici in atto."
            signed_by = 2 # Dott.ssa Bianchi
            signed_at = datetime.datetime.now() - datetime.timedelta(days=1)
            adm_status = 'discharged'

        service = random.choice(ris_services_pool)
        srv_name_lower = service["name"].lower()
        if 'risonanza' in srv_name_lower or 'rmn' in srv_name_lower or 'rm' in srv_name_lower:
            study_type = 'MRI'
        elif 'tc' in srv_name_lower or 'tac' in srv_name_lower or 'ct' in srv_name_lower:
            study_type = 'CT'
        elif 'ecografia' in srv_name_lower or 'eco' in srv_name_lower:
            study_type = 'ULTRASOUND'
        elif 'mammografia' in srv_name_lower:
            study_type = 'MAMMOGRAPHY'
        else:
            study_type = 'XRAY'

        h, m = rand_time()
        adm_date = today.replace(hour=h, minute=m) - datetime.timedelta(days=(random.randint(1, 5) if status != 'scheduled' else 0))
        
        admission_id = None
        
        cursor.execute("""
            INSERT INTO radiology_studies (patient_id, doctor_id, service_id, study_type, scheduled_at, status, report_text, signed_by, signed_at, tsrm_id, clinical_query)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            patient["id"], 2, service["id"], study_type, adm_date, status, 
            report_text, signed_by, signed_at, 5, "Quesito diagnostico generico per studio radiologico."
        ))
        study_id = cursor.lastrowid
        
        inv_num = f"FAT-2026-{invoice_count:04d}"
        invoice_count += 1
        
        price = service["price"] or 120.00
        paid_at = adm_date if inv_status == 'paid' else None
        pay_method = 'Carta' if inv_status == 'paid' else None
        amt_paid = price if inv_status == 'paid' else 0.0
        
        cursor.execute("""
            INSERT INTO invoices (admission_id, study_id, invoice_number, issue_date, subtotal, amount_due, amount_paid, payment_status, payment_method, paid_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (admission_id, study_id, inv_num, adm_date.date(), price, price, amt_paid, inv_status, pay_method, paid_at))
        
        if inv_status == 'paid':
            desc = f"Incasso prestazione RIS {service['name']} per {patient['first_name']} {patient['last_name']}"
            cursor.execute("""
                INSERT INTO prima_nota_movements (date, description, type, payment_method, amount)
                VALUES (%s, %s, %s, %s, %s)
            """, (adm_date.date(), desc[:250], 'entrata', pay_method, price))

    conn.commit()
    print("Seeded 23 RIS acceptances with admissions, studies, invoices, and payment tracking.")

# 11. Generate 20 LIS Acceptances
# - 4 "in corso" (processing): sample status received/processing, test pending
# - 4 "da prelevare": sample status collected, collected_at = NULL, test pending
# - 4 "complete da validare": sample status to_validate, test status completed, verified_by = NULL
# - 4 "validate ma non refertate": sample status completed, test completed, verified_by = 8, no official lab report
# - 4 "complete e refertate": sample status completed, test verified, official lab report exists
print("Seeding 20 LIS laboratory acceptances...")
lis_patient_pool = db_patients[23:43]
lis_services_pool = services_by_type["lis"]

if not lis_services_pool:
    print("WARNING: No LIS services found to seed laboratory studies!")
else:
    invoice_count = 100
    session_count = 1
    
    for idx, patient in enumerate(lis_patient_pool):
        h, m = rand_time()
        adm_date = today.replace(hour=h, minute=m) - datetime.timedelta(days=(random.randint(1, 4) if idx >= 8 else 0))
        
        if idx < 4:
            sample_status = 'processing'
            collected_at = adm_date
            collected_by = 4 # Nurse Neri
            test_status = 'pending'
            test_result = None
            verified_by = None
            verified_at = None
            report_status = None
            adm_status = 'active'
        elif idx < 8:
            sample_status = 'collected'
            collected_at = None
            collected_by = None
            test_status = 'pending'
            test_result = None
            verified_by = None
            verified_at = None
            report_status = None
            adm_status = 'active'
        elif idx < 12:
            sample_status = 'to_validate'
            collected_at = adm_date - datetime.timedelta(hours=2)
            collected_by = 4
            test_status = 'completed'
            test_result = f"{random.randint(75, 120)}"
            verified_by = None
            verified_at = None
            report_status = None
            adm_status = 'active'
        elif idx < 16:
            sample_status = 'completed'
            collected_at = adm_date - datetime.timedelta(hours=4)
            collected_by = 4
            test_status = 'completed'
            test_result = f"{random.randint(75, 120)}"
            verified_by = 8 # Biologo Chiara Lanza
            verified_at = adm_date + datetime.timedelta(hours=1)
            report_status = 'preliminary'
            adm_status = 'discharged'
        else:
            sample_status = 'completed'
            collected_at = adm_date - datetime.timedelta(hours=5)
            collected_by = 4
            test_status = 'completed'
            test_result = f"{random.randint(75, 120)}"
            verified_by = 8
            verified_at = adm_date + datetime.timedelta(hours=2)
            report_status = 'official'
            adm_status = 'discharged'

        srvs = random.sample(lis_services_pool, 2)
        session_uid = f"SESS-LIS-2026-{session_count:04d}"
        session_count += 1
        
        admission_id = None
        
        tubes_needed = {}
        for s in srvs:
            t_name = s["sample_type"] or "Siero (Attivatore - Rosso)"
            if t_name not in tubes_needed:
                tubes_needed[t_name] = []
            tubes_needed[t_name].append(s)
            
        sample_ids = []
        tot_price = 0.0
        
        for tube_name, services_in_tube in tubes_needed.items():
            barcode = f"2026{random.randint(100000, 999999):08d}"
            cursor.execute("""
                INSERT INTO lab_samples (patient_id, barcode, sample_type, status, session_uid, collected_at, collected_by, requesting_doctor)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (patient["id"], barcode, tube_name, sample_status, session_uid, collected_at, collected_by, "Dr. Medico Richiedente Esterno"))
            sample_id = cursor.lastrowid
            sample_ids.append(sample_id)
            
            for s in services_in_tube:
                tot_price += float(s["price"] or 15.0)
                ref_range = s["reference_range"] or "70-110"
                unit = s["unit"] or "mg/dL"
                
                cursor.execute("""
                    INSERT INTO lab_tests (sample_id, service_id, test_name, result_value, reference_range, unit, status, verified_by, verified_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (sample_id, s["id"], s["name"][:140], test_result, ref_range, unit, test_status, verified_by, verified_at))

        inv_num = f"FAT-LIS-{invoice_count:04d}"
        invoice_count += 1
        
        cursor.execute("""
            INSERT INTO invoices (admission_id, sample_id, invoice_number, issue_date, subtotal, amount_due, amount_paid, payment_status, payment_method, paid_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (admission_id, sample_ids[0], inv_num, adm_date.date(), tot_price, tot_price, tot_price, 'paid', 'Carta', adm_date))
        
        desc = f"Incasso accettazione LIS {session_uid} per {patient['first_name']} {patient['last_name']}"
        cursor.execute("""
            INSERT INTO prima_nota_movements (date, description, type, payment_method, amount)
            VALUES (%s, %s, %s, %s, %s)
        """, (adm_date.date(), desc[:250], 'entrata', 'Carta', tot_price))

        if report_status:
            released_at = (verified_at + datetime.timedelta(minutes=30)).isoformat() if verified_at else None
            cursor.execute("""
                INSERT INTO lab_reports (session_uid, status, notes, released_at, released_by)
                VALUES (%s, %s, %s, %s, %s)
            """, (session_uid, report_status, "Tutti i parametri rientrano nella norma clinica.", released_at, 8))

    conn.commit()
    print("Seeded 20 LIS acceptances with samples, tests, invoices, and reports.")

    # 12. Seed real Inpatient Admissions (Ricoveri)
    print("Seeding real inpatient admissions...")
    real_admissions = [
        (db_patients[43]["id"], today - datetime.timedelta(days=3), "Cardiologia", "Insufficienza cardiaca congestizia, monitoraggio parametri", "active"),
        (db_patients[44]["id"], today - datetime.timedelta(days=1), "Ortopedia", "Frattura del femore, decorso post-operatorio", "active"),
        (db_patients[45]["id"], today - datetime.timedelta(days=2), "Chirurgia Generale", "Addome acuto, post-appendicectomia", "active"),
        (db_patients[46]["id"], today - datetime.timedelta(days=10), "Medicina Int.", "Polmonite batterica, terapia antibiotica EV", "discharged"),
        (db_patients[47]["id"], today - datetime.timedelta(days=5), "Cardiologia", "Crisi ipertensiva risolta", "discharged")
    ]

    for pat_id, adm_date, dept, reason, status in real_admissions:
        discharge_date = adm_date + datetime.timedelta(days=7) if status == "discharged" else None
        cursor.execute("""
            INSERT INTO admissions (patient_id, admission_date, discharge_date, department, reason, status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (pat_id, adm_date, discharge_date, dept, reason, status))
    conn.commit()
    print("Successfully seeded 5 real inpatient admissions (3 active, 2 discharged).")

conn.close()
print("\nDATABASE RESET AND DEMO SEEDING COMPLETED SUCCESSFULLY!")
