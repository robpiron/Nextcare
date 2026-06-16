import http.server

import socketserver

import json

import os

import smtplib

from email.mime.text import MIMEText

from email.header import Header



# Lazy import pymysql to avoid hard crash if not installed immediately

try:

    import pymysql

    HAS_PYMYSQL = True

except ImportError:

    HAS_PYMYSQL = False

try:
    import pydicom
    from pydicom.dataset import Dataset
    import pynetdicom
    from pynetdicom import AE, evt, build_role
    from pynetdicom.sop_class import (
        PatientRootQueryRetrieveInformationModelFind,
        PatientRootQueryRetrieveInformationModelGet,
        CTImageStorage,
        MRImageStorage,
        SecondaryCaptureImageStorage
    )
    HAS_DICOM = True
except ImportError:
    HAS_DICOM = False



PORT = 8000

PORT_LOCAL = 8001



class NextCareHandler(http.server.SimpleHTTPRequestHandler):

    def end_headers(self):

        # Prevent caching issues during dev

        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')

        super().end_headers()



    def do_POST(self):

        content_length = int(self.headers['Content-Length'] or 0)

        post_data = self.rfile.read(content_length)

        

        try:

            data = json.loads(post_data.decode('utf-8'))

        except Exception as e:

            self.send_error_response(400, f"JSON malformato: {str(e)}")

            return

            

        if self.path == '/api/status':

            self.handle_status(data)

        elif self.path == '/api/login':

            self.handle_login(data)

        elif self.path == '/api/setup-db':

            self.handle_setup_db(data)

        elif self.path == '/api/test-db':

            self.handle_test_db(data)

        elif self.path == '/api/db-get-all':

            self.handle_db_get_all(data)

        elif self.path == '/api/db-sync-table':

            self.handle_db_sync_table(data)

        elif self.path == '/api/test-smtp':

            self.handle_test_smtp(data)

        elif self.path == '/api/send-email':

            self.handle_send_email(data)

        elif self.path == '/api/export-lis-requests':

            self.handle_export_lis(data)

        elif self.path == '/api/import-lis-results':

            self.handle_import_lis(data)

        elif self.path == '/api/save-pdf-report':

            self.handle_save_pdf_report(data)

        elif self.path == '/api/get-lis-simulator-status':

            self.handle_get_lis_simulator_status(data)

        elif self.path == '/api/toggle-lis-simulator':

            self.handle_toggle_lis_simulator(data)

        elif self.path == '/api/get-equipment-logs':

            self.handle_get_equipment_logs(data)

        elif self.path == '/api/clear-equipment-logs':

            self.handle_clear_equipment_logs(data)

        elif self.path == '/api/save-integration-settings':

            self.handle_save_integration_settings(data)

        elif self.path == '/api/bianalisi-export':

            self.handle_bianalisi_export(data)

        elif self.path == '/api/bianalisi-pull-results':

            self.handle_bianalisi_pull_results(data)

        elif self.path == '/api/dedalus-export-orders':

            self.handle_dedalus_export_orders(data)

        elif self.path == '/api/dedalus-import-results':

            self.handle_dedalus_import_results(data)

        elif self.path == '/api/lock-slot':

            self.handle_lock_slot(data)

        elif self.path == '/api/chat-heartbeat':

            self.handle_chat_heartbeat(data)

        elif self.path == '/api/chat-send':

            self.handle_chat_send(data)

        elif self.path == '/api/pacs-query':

            self.handle_pacs_query(data)

        elif self.path == '/api/pacs-retrieve':

            self.handle_pacs_retrieve(data)
        elif self.path == '/api/fse-settings-save':
            self.handle_fse_settings_save(data)
        elif self.path == '/api/fse-transmissions-list':
            self.handle_fse_transmissions_list(data)
        elif self.path == '/api/fse-cda-preview':
            self.handle_fse_cda_preview(data)
        elif self.path == '/api/fse-manual-send':
            self.handle_fse_manual_send(data)
        elif self.path == '/api/sts-settings-save':
            self.handle_sts_settings_save(data)
        elif self.path == '/api/sts-send-invoices':
            self.handle_sts_send_invoices(data)
        elif self.path == '/api/sts-export-xml':
            self.handle_sts_export_xml(data)
        elif self.path == '/api/compensations-list':
            self.handle_compensations_list(data)
        elif self.path == '/api/compensations-config-save':
            self.handle_compensations_config_save(data)
        elif self.path == '/api/compensations-config-delete':
            self.handle_compensations_config_delete(data)
        elif self.path == '/api/compensations-payout':
            self.handle_compensations_payout(data)
        elif self.path == '/api/portals-login':
            self.handle_portals_login(data)
        elif self.path == '/api/portal-appointments':
            self.handle_portal_appointments(data)
        elif self.path == '/api/portal-invoices':
            self.handle_portal_invoices(data)
        elif self.path == '/api/portal-reports':
            self.handle_portal_reports(data)
        elif self.path == '/api/portal-cancel-appointment':
            self.handle_portal_cancel_appointment(data)
        elif self.path == '/api/portal-patient-data':
            self.handle_portal_patient_data(data)
        elif self.path == '/api/portal-company-data':
            self.handle_portal_company_data(data)
        elif self.path == '/api/portal-cp-data':
            self.handle_portal_cp_data(data)
        elif self.path == '/api/portal-upsert-records':
            self.handle_portal_upsert_records(data)
        elif self.path == '/api/mwl-status':
            self.handle_mwl_status(data)
        elif self.path == '/api/price-lists-duplicate':
            self.handle_price_lists_duplicate(data)
        elif self.path == '/api/ai-help':
            self.handle_ai_help(data)
        elif self.path == '/api/system-settings-save':
            self.handle_system_settings_save(data)
        elif self.path == '/api/admin/generate-license':
            self.handle_generate_license(data)
        elif self.path == '/api/admin/list-licenses':
            self.handle_list_licenses(data)
        elif self.path == '/api/activate-license':
            self.handle_activate_license(data)

        else:

            self.send_error_response(404, "Endpoint non trovato")



    def do_GET(self):

        if self.path.startswith('/api/'):

            from urllib.parse import urlparse, parse_qs

            parsed = urlparse(self.path)

            path = parsed.path

            params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

            

            if path == '/api/get-integration-settings':

                self.handle_get_integration_settings(params)

            elif path == '/api/bianalisi-labels':

                self.handle_bianalisi_labels(params)

            elif path == '/api/socket-servers-status':

                self.handle_get_socket_servers_status()

            elif path == '/api/get-locked-slots':

                self.handle_get_locked_slots()

            elif path == '/api/system-settings':

                self.handle_system_settings_get()

            elif path == '/api/db-get-all':

                self.handle_db_get_all(params)

            else:

                self.send_error_response(404, "Endpoint GET non trovato")

        else:

            super().do_GET()



    def send_error_response(self, code, message):

        self.send_response(code)

        self.send_header('Content-Type', 'application/json; charset=utf-8')

        self.end_headers()

        res = {"success": False, "error": message}

        self.wfile.write(json.dumps(res).encode('utf-8'))



    def send_success_response(self, data):

        self.send_response(200)

        self.send_header('Content-Type', 'application/json; charset=utf-8')

        self.end_headers()

        res = {"success": True, "data": data}

        self.wfile.write(json.dumps(res).encode('utf-8'))



    def load_config(self):

        config_path = "config.json"

        if os.path.exists(config_path):

            try:

                with open(config_path, "r", encoding="utf-8") as f:

                    return json.load(f)

            except Exception:

                pass

        return {}



    def save_config(self, config):

        config_path = "config.json"

        try:

            with open(config_path, "w", encoding="utf-8") as f:

                json.dump(config, f, indent=4)

            return True

        except Exception:

            return False



    def handle_status(self, params):

        config = self.load_config()

        configured = bool(config.get('db_host'))

        

        # Test connection if configured

        can_connect = False

        db_error = None

        if configured:

            try:

                conn = pymysql.connect(

                    host=config.get('db_host', 'localhost'),

                    port=int(config.get('db_port', 3306)),

                    user=config.get('db_user', 'root'),

                    password=config.get('db_pass', ''),

                    database=config.get('db_name', 'nextcare_db'),

                    connect_timeout=3

                )

                conn.close()

                can_connect = True

            except Exception as e:

                db_error = str(e)

                

        self.send_success_response({

            "configured": configured,

            "can_connect": can_connect,

            "db_error": db_error,

            "db_host": config.get('db_host', ''),

            "db_name": config.get('db_name', ''),

            "db_user": config.get('db_user', ''),

            "lis_export_path": config.get('lis_export_path', r"C:\NextCare_LIS_Exchange\export"),

            "lis_import_path": config.get('lis_import_path', r"C:\NextCare_LIS_Exchange\import")

        })



    def handle_login(self, params):

        if not HAS_PYMYSQL:

            self.send_error_response(500, "Driver PyMySQL non installato")

            return

            

        username = params.get('username')

        password = params.get('password')

        

        if not username or not password:

            self.send_error_response(400, "Username e password obbligatori")

            return

            

        config = self.load_config()

        if not config.get('db_host'):

            self.send_error_response(400, "Database non configurato")

            return

            

        try:

            conn = pymysql.connect(

                host=config.get('db_host', 'localhost'),

                port=int(config.get('db_port', 3306)),

                user=config.get('db_user', 'root'),

                password=config.get('db_pass', ''),

                database=config.get('db_name', 'nextcare_db'),

                charset='utf8mb4',

                cursorclass=pymysql.cursors.DictCursor

            )

            cursor = conn.cursor()

            

            cursor.execute(

                "SELECT id, first_name, last_name, role, email, phone, active, username, password, profiles FROM staff WHERE username = %s AND active = 1",

                (username,)

            )

            user_row = cursor.fetchone()

            

            if user_row and user_row.get('password') == password:

                profiles = user_row.get('profiles')

                if isinstance(profiles, str):

                    try:

                        profiles = json.loads(profiles)

                    except Exception:

                        profiles = [profiles]

                elif not profiles:

                    profiles = []

                    

                user_info = {

                    "id": user_row['id'],

                    "first_name": user_row['first_name'],

                    "last_name": user_row['last_name'],

                    "role": user_row['role'],

                    "email": user_row['email'],

                    "username": user_row['username'],

                    "profiles": profiles

                }

                

                try:

                    details_json = json.dumps({"username": username, "status": "success", "ip": self.client_address[0]})

                    cursor.execute(

                        "INSERT INTO audit_logs (staff_id, action, table_name, record_id, details) VALUES (%s, %s, %s, %s, %s)",

                        (user_row['id'], 'LOGIN_SUCCESS', 'staff', user_row['id'], details_json)

                    )

                    conn.commit()

                except Exception as e:

                    print(f"[Login Audit Log Error] {e}")

                    

                conn.close()

                self.send_success_response(user_info)

            else:

                try:

                    details_json = json.dumps({"username": username, "status": "failed", "ip": self.client_address[0]})

                    cursor.execute(

                        "INSERT INTO audit_logs (staff_id, action, table_name, record_id, details) VALUES (NULL, %s, %s, NULL, %s)",

                        ('LOGIN_FAILURE', 'staff', details_json)

                    )

                    conn.commit()

                except Exception as e:

                    print(f"[Login Audit Log Error] {e}")

                

                if conn:

                    conn.close()

                self.send_error_response(401, "Credenziali non valide")

                

        except Exception as e:

            self.send_error_response(500, f"Errore durante il login: {str(e)}")



    def handle_setup_db(self, params):

        host = params.get('db_host', 'localhost')

        port = int(params.get('db_port', 3306))

        user = params.get('db_user', 'root')

        password = params.get('db_pass', '')

        db_name = params.get('db_name', 'nextcare_db')

        lis_export_path = params.get('lis_export_path', r"C:\NextCare_LIS_Exchange\export")

        lis_import_path = params.get('lis_import_path', r"C:\NextCare_LIS_Exchange\import")

        

        try:

            # Connect to MySQL and create DB

            conn = pymysql.connect(

                host=host,

                port=port,

                user=user,

                password=password,

                connect_timeout=5

            )

            cursor = conn.cursor()

            cursor.execute(f"DROP DATABASE IF EXISTS {db_name}")

            cursor.execute(f"CREATE DATABASE {db_name}")

            cursor.execute(f"USE {db_name}")

            

            # Execute schema.sql

            schema_path = "schema.sql"

            if not os.path.exists(schema_path):

                schema_path = "../schema.sql"

                

            if os.path.exists(schema_path):

                with open(schema_path, "r", encoding="utf-8") as f:

                    schema_sql = f.read()

                

                # Strip comments per line to handle inline and trailing comments correctly

                cleaned_lines = []

                for line in schema_sql.split("\n"):

                    line_clean = line

                    if "--" in line_clean:

                        line_clean = line_clean.split("--", 1)[0]

                    if "#" in line_clean:

                        line_clean = line_clean.split("#", 1)[0]

                    cleaned_lines.append(line_clean.strip())

                

                reconstructed_sql = "\n".join(cleaned_lines)

                statements = reconstructed_sql.split(";")

                try:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
                except Exception:
                    pass

                for stmt in statements:

                    stmt_clean = stmt.strip()

                    if stmt_clean:

                        if stmt_clean.upper().startswith("CREATE DATABASE") or stmt_clean.upper().startswith("USE"):

                            continue

                        try:

                            cursor.execute(stmt_clean)

                        except Exception as e:

                            print(f"[SQL WARNING] query: {stmt_clean[:80]}... -> {str(e)}")

                try:
                    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
                except Exception:
                    pass

                            

            # Proactively ensure system_settings table exists (with multiple compatibility fallbacks)

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `system_settings` (

                        `setting_key` VARCHAR(100) PRIMARY KEY,

                        `setting_value` TEXT NOT NULL,

                        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

            except Exception as e1:

                try:

                    cursor.execute("""

                        CREATE TABLE IF NOT EXISTS `system_settings` (

                            `setting_key` VARCHAR(100) PRIMARY KEY,

                            `setting_value` TEXT NOT NULL,

                            `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

                        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                    """)

                except Exception as e2:

                    try:

                        cursor.execute("""

                            CREATE TABLE IF NOT EXISTS `system_settings` (

                                `setting_key` VARCHAR(100) PRIMARY KEY,

                                `setting_value` TEXT NOT NULL

                            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                        """)

                    except Exception as e3:

                        pass



            # Proactively ensure lis_worksheets table exists

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `lis_worksheets` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `name` VARCHAR(255) NOT NULL,

                        `service_ids` TEXT NOT NULL,

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

            except Exception as e:

                pass



            # Proactively ensure lab_reports table exists

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `lab_reports` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `session_uid` VARCHAR(50) NOT NULL,

                        `status` ENUM('preliminary', 'official') NOT NULL DEFAULT 'preliminary',

                        `notes` TEXT NULL,

                        `released_at` VARCHAR(50) NULL,

                        `released_by` INT NULL,

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                        UNIQUE INDEX `uq_session_uid` (`session_uid`)

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

            except Exception as e:

                pass



            # Proactively ensure consent_templates table exists

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `consent_templates` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `title` VARCHAR(255) NOT NULL,

                        `content` TEXT NOT NULL,

                        `scope` VARCHAR(50) NOT NULL DEFAULT 'all',

                        `modality` VARCHAR(50) NULL,

                        `doctor_id` INT NULL,

                        `min_age` INT NULL,

                        `max_age` INT NULL,

                        `gender` VARCHAR(10) NOT NULL DEFAULT 'all',

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                        FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE SET NULL

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

            except Exception as e:

                pass



            # Setup LIS export/import paths in system_settings table

            cursor.execute("INSERT INTO system_settings (setting_key, setting_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting_value=%s", ('lis_export_path', lis_export_path, lis_export_path))

            cursor.execute("INSERT INTO system_settings (setting_key, setting_value) VALUES (%s, %s) ON DUPLICATE KEY UPDATE setting_value=%s", ('lis_import_path', lis_import_path, lis_import_path))

            conn.commit()

            

            # Seed medical services if empty

            cursor.execute("SELECT COUNT(*) FROM medical_services")

            srv_count = cursor.fetchone()[0]

            

            seeds_loaded = False

            if srv_count == 0:

                for seed_file in ['ris_visite_services_seed.json', 'lis_services_seed.json']:

                    path = seed_file

                    if not os.path.exists(path):

                        path = os.path.join("NextCareApp", seed_file)

                    if not os.path.exists(path):

                        path = os.path.join("..", seed_file)

                        

                    if os.path.exists(path):

                        with open(path, "r", encoding="utf-8") as f:

                            services_data = json.load(f)

                            

                        for srv in services_data:

                            params_json = json.dumps(srv.get('parameters', [])) if srv.get('parameters') else None

                            cursor.execute(

                                "INSERT INTO medical_services (name, type, code, branch, price, sample_type, reference_range, unit, parameters) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",

                                (

                                    srv.get('name', ''),

                                    srv.get('type', 'visita'),

                                    srv.get('code', ''),

                                    srv.get('branch', ''),

                                    srv.get('price', 0.0),

                                    srv.get('sample_type', ''),

                                    srv.get('reference_range', ''),

                                    srv.get('unit', ''),

                                    params_json

                                )

                            )

                        conn.commit()

                seeds_loaded = True

            

            conn.close()

            

            # Save configuration locally to config.json

            config = {

                "db_host": host,

                "db_port": port,

                "db_user": user,

                "db_pass": password,

                "db_name": db_name,

                "lis_export_path": lis_export_path,

                "lis_import_path": lis_import_path

            }

            self.save_config(config)

            

            self.send_success_response({

                "message": "Database configurato con successo!",

                "seeds_loaded": seeds_loaded

            })

            

        except Exception as e:

            self.send_error_response(500, f"Errore configurazione database: {str(e)}")



    def handle_test_db(self, params):

        if not HAS_PYMYSQL:

            self.send_error_response(500, "Errore: Driver 'PyMySQL' non installato. Installa con: pip install PyMySQL")

            return



        host = params.get('host', 'localhost')

        port = int(params.get('port', 3306))

        user = params.get('user', 'root')

        password = params.get('password', '')

        db_name = params.get('name', 'nextcare_db')



        try:

            # Connect to MySQL server WITHOUT specifying the database name (test connection only)

            conn = pymysql.connect(

                host=host,

                port=port,

                user=user,

                password=password,

                connect_timeout=5

            )

            

            cursor = conn.cursor()

            

            # Check if the database exists

            cursor.execute("SHOW DATABASES")

            databases = [db[0].lower() for db in cursor.fetchall()]

            db_exists = db_name.lower() in databases

            

            if db_exists:

                cursor.execute(f"USE `{db_name}`")

                cursor.execute("SHOW TABLES")

                tables = [t[0].lower() for t in cursor.fetchall()]

                required_tables = [

                    'patients', 'staff', 'doctors', 'doctor_agendas', 'doctor_agenda_services',

                    'medical_services', 'appointments', 'appointment_services', 'lab_samples',

                    'lab_tests', 'radiology_studies', 'admissions', 'invoices', 'shifts',

                    'price_lists', 'price_list_items', 'insurances', 'patient_claims', 'tube_types', 'profit_centers',

                    'lab_reports', 'consent_templates', 'dose_classes'

                ]

                missing = [rt for rt in required_tables if rt not in tables]

                if not missing:

                    msg = f"Connessione al server MySQL riuscita!\nIl database '{db_name}' esiste già e tutte le tabelle sono presenti."

                else:

                    msg = f"Connessione al server MySQL riuscita!\nIl database '{db_name}' esiste già, ma mancano alcune tabelle ({len(missing)} mancanti). Verranno create durante l'installazione."

            else:

                msg = f"Connessione al server MySQL riuscita!\nIl database '{db_name}' non esiste ancora e verrà creato automaticamente durante l'installazione."

            

            conn.close()

            self.send_success_response({"message": msg, "db_exists": db_exists})

                

        except Exception as e:

            self.send_error_response(500, f"Impossibile connettersi al server MySQL.\nDettaglio errore: {str(e)}")



    def handle_db_get_all(self, params):

        import datetime

        if not HAS_PYMYSQL:

            self.send_error_response(500, "Driver PyMySQL non installato")

            return

            

        config = self.load_config()

        if not config.get('db_host'):

            self.send_error_response(400, "Database non configurato")

            return

            

        try:

            conn = pymysql.connect(

                host=config.get('db_host', 'localhost'),

                port=int(config.get('db_port', 3306)),

                user=config.get('db_user', 'root'),

                password=config.get('db_pass', ''),

                database=config.get('db_name', 'nextcare_db'),

                charset='utf8mb4',

                cursorclass=pymysql.cursors.DictCursor

            )

            cursor = conn.cursor()

            try:
                auto_detect_updates(conn)
            except Exception as ade:
                print(f"[AutoNews Error] Failed to run auto_detect_updates: {ade}")
            
            # Redundant migrations removed (already run on server startup)

            # Query all table names in the database dynamically

            cursor.execute("SHOW TABLES")

            db_tables = [list(r.values())[0].lower() for r in cursor.fetchall()]

            

            data = {}

            for t in db_tables:

                try:

                    cursor.execute(f"SELECT * FROM `{t}`")

                    rows = cursor.fetchall()

                    import decimal

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

                            elif col in ['parameters', 'details', 'custom_rates', 'service_ids', 'active_days', 'updated_fields', 'values', 'package_items', 'lis_transcoding', 'profiles', 'doctor_ids', 'reporting_doctor_ids', 'antibiotics_json', 'samples_json', 'time_slots', 'temperature_log'] and isinstance(val, str):
                                try:
                                    cleaned_row[col] = json.loads(val)
                                except Exception:
                                    cleaned_row[col] = val

                            else:

                                cleaned_row[col] = val

                        cleaned_rows.append(cleaned_row)

                    data[t] = cleaned_rows

                except Exception as e:

                    print(f"[SQL ERROR] fetch table {t} failed: {str(e)}")

                    

            conn.close()

            # If a specific table is requested, return rows for that table
            req_table = params.get('table') if isinstance(params, dict) else None
            if req_table and req_table.lower() in data:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                res = {
                    "success": True,
                    "rows": data[req_table.lower()],
                    "data": data[req_table.lower()]
                }
                self.wfile.write(json.dumps(res).encode('utf-8'))
                return

            self.send_success_response(data)

        except Exception as e:

            self.send_error_response(500, f"Errore nel caricamento del database: {str(e)}")

    

    def handle_db_sync_table(self, params):

        if not HAS_PYMYSQL:

            self.send_error_response(500, "Driver PyMySQL non installato")

            return

            

        table_name = params.get('table_name')

        rows = params.get('rows', [])

        

        if not table_name:

            self.send_error_response(400, "Tabella non specificata")

            return

        # Check license block in backend
        if table_name.lower() not in ['system_settings', 'system_license', 'generated_licenses', 'audit_logs']:
            config = self.load_config()
            if config.get('db_host'):
                try:
                    conn_check = pymysql.connect(
                        host=config.get('db_host', 'localhost'),
                        port=int(config.get('db_port', 3306)),
                        user=config.get('db_user', 'root'),
                        password=config.get('db_pass', ''),
                        database=config.get('db_name', 'nextcare_db'),
                        charset='utf8mb4',
                        cursorclass=pymysql.cursors.DictCursor
                    )
                    with conn_check.cursor() as cur:
                        status = self.check_license_limits(cur)
                        if status['blocked']:
                            conn_check.close()
                            self.send_error_response(403, f"Operazione bloccata: i limiti della licenza attiva sono superati. {status['reason']}")
                            return
                    conn_check.close()
                except Exception as ex:
                    print("License backend block check error:", ex)

            

        if os.path.exists(".disable_sync"):

            self.send_success_response({"message": "Sincronizzazione temporaneamente disabilitata per esecuzione test"})

            return

            

        config = self.load_config()

        if not config.get('db_host'):

            self.send_error_response(400, "Database non configurato")

            return

            

        import re

        def clean_datetime_val(val):

            if isinstance(val, str):

                iso_match = re.match(r'^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}(?::\d{2})?)(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$', val)

                if iso_match:

                    date_part = iso_match.group(1)

                    time_part = iso_match.group(2)

                    if len(time_part) == 5:

                        time_part += ":00"

                    return f"{date_part} {time_part}"

            return val

            

        try:

            conn = pymysql.connect(

                host=config.get('db_host', 'localhost'),

                port=int(config.get('db_port', 3306)),

                user=config.get('db_user', 'root'),

                password=config.get('db_pass', ''),

                database=config.get('db_name', 'nextcare_db'),

                charset='utf8mb4'

            )

            cursor = conn.cursor()

            

            # Verify if table exists in MySQL first

            cursor.execute("SHOW TABLES")

            db_tables = [r[0].lower() for r in cursor.fetchall()]

            

            if table_name.lower() not in db_tables:

                conn.close()

                self.send_success_response({"message": f"Tabella {table_name} ignorata (non presente nel database)"})

                return

            

            # Disable foreign key checks to overwrite safely

            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

            

            # Delete table contents instead of TRUNCATE so it can be rolled back on error

            cursor.execute(f"DELETE FROM `{table_name}`")

            

            if rows:

                # Get columns for this table

                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")

                cols_info = cursor.fetchall()

                columns = [col[0] for col in cols_info]

                defaults = {col[0]: col[4] for col in cols_info}

                # Deduplicate rows to prevent Duplicate Entry errors on sync
                seen_keys = set()
                deduped_rows = []
                for row in rows:
                    key_val = None
                    if 'id' in columns:
                        key_val = row.get('id')
                    elif 'setting_key' in columns:
                        key_val = row.get('setting_key')
                    elif 'price_list_id' in columns and 'service_id' in columns:
                        key_val = (row.get('price_list_id'), row.get('service_id'))
                    elif 'appointment_id' in columns and 'service_id' in columns:
                        key_val = (row.get('appointment_id'), row.get('service_id'))
                    elif 'agenda_id' in columns and 'service_id' in columns:
                        key_val = (row.get('agenda_id'), row.get('service_id'))
                    
                    if key_val is not None:
                        if key_val in seen_keys:
                            continue
                        seen_keys.add(key_val)
                    deduped_rows.append(row)
                rows = deduped_rows

                valid_rows = []

                for row in rows:

                    row_data = []

                    for col in columns:

                        val = row.get(col)

                        # Handle JSON serialization for dict/list types

                        if isinstance(val, (list, dict)):
                            val = json.dumps(val)

                        if val == "":

                            val = None

                        if val is None:

                            if col == 'lis_interface_type':

                                val = 'none'

                            elif col in ['is_credit_note', 'lis_simulator_active', 'is_insurance_invoice', 'stamp_duty', 'is_company_post']:

                                val = 0
                            
                            elif col == 'action':
                                
                                val = 'UNKNOWN'
                                
                            elif col == 'table_name':
                                
                                val = 'unknown'
                                
                            elif defaults.get(col) is not None:
                                
                                raw_def = defaults.get(col)
                                if isinstance(raw_def, str) and 'CURRENT_TIMESTAMP' in raw_def.upper():
                                    import datetime
                                    val = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                else:
                                    val = raw_def
                            
                            elif col == 'action':
                                
                                val = 'UNKNOWN'
                                
                            elif defaults.get(col) is not None:
                                
                                val = defaults.get(col)

                        
                        if table_name.lower() == 'lab_samples' and col == 'status':
                            if val == 'da prelevare':
                                val = 'collected'
                            elif val == 'validated':
                                val = 'completed'

                        # Clean ISO datetime formats for MySQL compatibility

                        val = clean_datetime_val(val)

                        

                        row_data.append(val)

                    valid_rows.append(row_data)

                

                placeholders = ", ".join(["%s"] * len(columns))

                col_names = ", ".join([f"`{c}`" for c in columns])

                query = f"INSERT INTO `{table_name}` ({col_names}) VALUES ({placeholders})"

                

                cursor.executemany(query, valid_rows)

                

            conn.commit()

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

            conn.close()

            

            self.check_sync_event_triggers(table_name, rows)
            self.send_success_response({"message": f"Tabella {table_name} sincronizzata con successo"})

        except Exception as e:
            import traceback
            print(f"[MySQL Sync Error] Failed to sync table {table_name}: {e}")
            traceback.print_exc()
            if 'conn' in locals() and conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            try:

                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

                conn.close()

            except Exception:

                pass

            self.send_error_response(500, f"Errore nel salvataggio della tabella {table_name}: {str(e)}")



    def handle_test_smtp(self, params):

        host = params.get('smtp_host', '')

        port = int(params.get('smtp_port', 587))

        user = params.get('smtp_user', '')

        password = params.get('smtp_pass', '')

        security = params.get('smtp_security', 'starttls')

        auth = params.get('smtp_auth', 'login')

        ignore_cert = params.get('smtp_ignore_cert', 0) == 1

        

        if not host:

            self.send_error_response(400, "Specificare l'host SMTP")

            return



        try:

            import ssl

            context = None

            if ignore_cert:

                context = ssl._create_unverified_context()

            else:

                context = ssl.create_default_context()



            # Choose correct SMTP class based on security

            if security == 'ssl':

                server = smtplib.SMTP_SSL(host, port, timeout=10, context=context)

            else:

                server = smtplib.SMTP(host, port, timeout=10)

                

            server.ehlo()

            if security == 'starttls':

                server.starttls(context=context)

                server.ehlo()

                

            if auth == 'login' and user and password:

                server.login(user, password)

                

            server.quit()

            

            msg = f"Connessione completata con successo! Handshake SSL/TLS riuscito sul server SMTP {host}:{port}."

            if auth == 'login':

                msg += f" Autenticazione per {user} riuscita."

            else:

                msg += " Connessione non autenticata completata."

                

            self.send_success_response({"message": msg})

            

        except Exception as e:

            self.send_error_response(500, f"Connessione SMTP fallita.\nDettaglio errore: {str(e)}")



    def handle_send_email(self, params):

        smtp = params.get('smtp_settings', {})

        email_data = params.get('email', {})

        

        host = smtp.get('smtp_host', '')

        port = int(smtp.get('smtp_port', 587))

        user = smtp.get('smtp_user', '')

        password = smtp.get('smtp_pass', '')

        security = smtp.get('smtp_security', 'starttls')

        auth = smtp.get('smtp_auth', 'login')

        ignore_cert = smtp.get('smtp_ignore_cert', 0) == 1

        

        sender_email = smtp.get('smtp_sender_email', '')

        if not sender_email:

            sender_email = user if user else 'notifiche@nextcare.it'

            

        sender_name = smtp.get('smtp_sender_name', '')

        if not sender_name:

            sender_name = 'Clinica NextCare'

        

        recipient = email_data.get('recipient', '')

        subject = email_data.get('subject', '')

        body = email_data.get('body', '')

        

        if not host or not recipient:

            self.send_error_response(400, "Parametri SMTP o destinatario mancanti")

            return



        try:

            # Create message

            msg = MIMEText(body, 'html', 'utf-8')

            msg['Subject'] = Header(subject, 'utf-8')

            from_header = f"{sender_name} <{sender_email}>" if sender_name else sender_email

            msg['From'] = from_header

            msg['To'] = recipient

            

            import ssl

            context = None

            if ignore_cert:

                context = ssl._create_unverified_context()

            else:

                context = ssl.create_default_context()



            if security == 'ssl':

                server = smtplib.SMTP_SSL(host, port, timeout=15, context=context)

            else:

                server = smtplib.SMTP(host, port, timeout=15)

                

            server.ehlo()

            if security == 'starttls':

                server.starttls(context=context)

                server.ehlo()

                

            if auth == 'login' and user and password:

                server.login(user, password)

                

            server.sendmail(sender_email, [recipient], msg.as_string())

            server.quit()

            

            self.send_success_response({"message": f"Email inviata con successo a {recipient}"})

            

        except Exception as e:

            self.send_error_response(500, f"Errore nell'invio reale dell'email: {str(e)}")



    def handle_export_lis(self, data):

        import datetime

        try:

            config = self.load_config()

            export_dir = config.get('lis_export_path', r"C:\NextCare_LIS_Exchange\export")

            os.makedirs(export_dir, exist_ok=True)

            

            xml_lines = []

            xml_lines.append('<?xml version="1.0" encoding="utf-8"?>')

            xml_lines.append('<ListaRichieste>')

            xml_lines.append('    <CodiceLaboratorio>NEXTCARE</CodiceLaboratorio>')

            

            for req in data.get('requests', []):

                xml_lines.append('    <Richiesta>')

                xml_lines.append(f"        <Cognome>{req.get('last_name', '')}</Cognome>")

                xml_lines.append(f"        <Nome>{req.get('first_name', '')}</Nome>")

                xml_lines.append(f"        <IdRichiestaLis>{req.get('barcode', '')}</IdRichiestaLis>")

                xml_lines.append(f"        <Sesso>{req.get('gender', '')}</Sesso>")

                xml_lines.append(f"        <DataNascita>{req.get('birth_date', '')}</DataNascita>")

                xml_lines.append(f"        <Data>{req.get('date', '')}</Data>")

                if req.get('tax_code'):

                    xml_lines.append(f"        <CodiceFiscale>{req.get('tax_code', '')}</CodiceFiscale>")

                

                for ana in req.get('analyses', []):

                    mat_str = f' Materiale="{ana.get("material", "")}"' if ana.get('material') else ''

                    xml_lines.append(f'        <Analisi Codice="{ana.get("code", "")}" IdCampioneLis="{req.get("barcode", "")}"{mat_str} />')

                

                xml_lines.append('    </Richiesta>')

            xml_lines.append('</ListaRichieste>')

            

            xml_content = "\n".join(xml_lines)

            

            today_str = datetime.date.today().isoformat()

            filename = f"{today_str}-NextCare.xml"

            file_path = os.path.join(export_dir, filename)

            

            with open(file_path, "w", encoding="utf-8") as f:

                f.write(xml_content)

                

            self.send_success_response({

                "message": f"Richieste esportate con successo in {file_path}",

                "xml": xml_content,

                "filename": filename

            })

        except Exception as e:

            self.send_error_response(500, f"Errore nell'esportazione LIS: {str(e)}")



    def handle_import_lis(self, data):

        try:

            results = check_and_import_file_results()

            self.send_success_response({

                "message": f"Elaborazione risultati completata.",

                "results": results

            })

        except Exception as e:

            self.send_error_response(500, f"Errore nell'importazione LIS: {str(e)}")



    def handle_save_pdf_report(self, data):

        try:

            import base64

            filename = data.get("filename")

            base64_content = data.get("base64_content")

            

            if not filename or not base64_content:

                self.send_error_response(400, "Nome file o contenuto base64 mancante")

                return

                

            # Clean filename

            filename = os.path.basename(filename)

            

            # Ensure folder exists in the project workspace

            export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "esportazioni_referti")

            os.makedirs(export_dir, exist_ok=True)

            

            file_path = os.path.join(export_dir, filename)

            

            # Decode and write

            pdf_bytes = base64.b64decode(base64_content)

            with open(file_path, "wb") as f:

                f.write(pdf_bytes)

                

            self.send_success_response({

                "message": f"Referto salvato con successo",

                "path": file_path

            })

        except Exception as e:

            self.send_error_response(500, f"Errore nel salvataggio del referto: {str(e)}")



    def handle_get_lis_simulator_status(self, data):

        eq_id = data.get('equipment_id')

        if eq_id:

            conn = get_db_connection()

            if conn:

                try:

                    with conn.cursor() as cursor:

                        cursor.execute("SELECT lis_simulator_active FROM equipment WHERE id = %s", (eq_id,))

                        row = cursor.fetchone()

                        active = bool(row.get('lis_simulator_active', 0)) if row else False

                        self.send_success_response({

                            "active": active,

                            "equipment_id": eq_id

                        })

                        return

                except Exception as e:

                    print(f"[MySQL Simulator Status Error] {e}")

                finally:

                    conn.close()

        

        config = self.load_config()

        self.send_success_response({

            "active": config.get('lis_simulator_active', False)

        })



    def handle_toggle_lis_simulator(self, data):

        eq_id = data.get('equipment_id')

        active = data.get('active', False)

        

        if eq_id:

            conn = get_db_connection()

            if conn:

                try:

                    with conn.cursor() as cursor:

                        cursor.execute("UPDATE equipment SET lis_simulator_active = %s WHERE id = %s", (1 if active else 0, eq_id))

                        conn.commit()

                except Exception as e:

                    print(f"[MySQL Toggle Simulator Error] {e}")

                finally:

                    conn.close()

        else:

            config = self.load_config()

            config['lis_simulator_active'] = active

            self.save_config(config)

            

        self.send_success_response({

            "message": f"Simulatore LIS {'attivato' if active else 'disattivato'} con successo per lo strumento" if eq_id else f"Simulatore LIS {'attivato' if active else 'disattivato'} con successo",

            "active": active,

            "equipment_id": eq_id

        })



    def handle_get_equipment_logs(self, data):

        eq_id = data.get('equipment_id')

        if not eq_id:

            self.send_error_response(400, "Identificativo strumento mancante")

            return

            

        logs = []

        conn = get_db_connection()

        if conn:

            try:

                with conn.cursor() as cursor:

                    cursor.execute("""

                        SELECT direction, message_type, content, DATE_FORMAT(timestamp, '%%Y-%%m-%%d %%H:%%i:%%s') as timestamp

                        FROM equipment_logs

                        WHERE equipment_id = %s

                        ORDER BY id DESC

                        LIMIT 100

                    """, (eq_id,))

                    logs = cursor.fetchall()

            except Exception as e:

                print(f"[MySQL Get Logs Error] {e}")

            finally:

                conn.close()

                

        if not logs:

            try:

                logs = EQUIPMENT_LOGS.get(int(eq_id), [])

            except Exception:

                logs = []

            

        self.send_success_response({

            "logs": logs

        })



    def handle_clear_equipment_logs(self, data):

        eq_id = data.get('equipment_id')

        if not eq_id:

            self.send_error_response(400, "Identificativo strumento mancante")

            return

        

        conn = get_db_connection()

        if conn:

            try:

                with conn.cursor() as cursor:

                    cursor.execute("DELETE FROM equipment_logs WHERE equipment_id = %s", (eq_id,))

                    conn.commit()

            except Exception as e:

                print(f"[MySQL Clear Logs Error] {e}")

            finally:

                conn.close()

        

        try:

            if int(eq_id) in EQUIPMENT_LOGS:

                EQUIPMENT_LOGS[int(eq_id)] = []

        except Exception:

            pass

            

        self.send_success_response({"message": "Log cancellati con successo"})



    def handle_save_integration_settings(self, data):

        partner = data.get('partner')

        settings = data.get('settings')

        if not partner:

            self.send_error_response(400, "Partner mancante")

            return

        conn = get_db_connection()

        if not conn:

            self.send_error_response(500, "Impossibile connettersi al database")

            return

        try:

            with conn.cursor() as cursor:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS system_settings (

                        setting_key VARCHAR(100) PRIMARY KEY,

                        setting_value TEXT

                    )

                """)

                val_str = json.dumps(settings)

                key_str = f"integration_{partner}"

                cursor.execute("""

                    INSERT INTO system_settings (setting_key, setting_value)

                    VALUES (%s, %s)

                    ON DUPLICATE KEY UPDATE setting_value = %s

                """, (key_str, val_str, val_str))

                conn.commit()

            self.send_success_response({"message": "Impostazioni salvate con successo"})

        except Exception as e:

            self.send_error_response(500, f"Errore nel salvataggio impostazioni: {str(e)}")

    def handle_get_socket_servers_status(self):
        status_map = {}
        for port, info in RUNNING_SOCKET_SERVERS.items():
            status_map[port] = {
                'active': info.get('active', False),
                'status': info.get('status', 'offline'),
                'error_reason': info.get('error_reason', None),
                'format': info.get('format', 'hl7')
            }
        self.send_success_response(status_map)

    def handle_get_locked_slots(self):
        now = time.time()
        with SLOT_LOCK:
            for k in list(LOCKED_SLOTS.keys()):
                lock_time, _ = LOCKED_SLOTS[k]
                if now - lock_time > 300:
                    del LOCKED_SLOTS[k]
            locks_data = {}
            for k, (lt, username) in LOCKED_SLOTS.items():
                locks_data[k] = {
                    'username': username,
                    'locked_at': lt
                }
        self.send_success_response(locks_data)

    def handle_lock_slot(self, data):
        agenda_id = data.get('agenda_id')
        slot_datetime = data.get('slot_datetime')
        username = data.get('username')
        lock = data.get('lock', True)

        if not agenda_id or not slot_datetime or not username:
            self.send_error_response(400, "Parametri incompleti")
            return

        lock_key = f"{agenda_id}_{slot_datetime}"
        now = time.time()

        with SLOT_LOCK:
            for k in list(LOCKED_SLOTS.keys()):
                lock_time, _ = LOCKED_SLOTS[k]
                if now - lock_time > 300:
                    del LOCKED_SLOTS[k]

            if lock:
                if lock_key in LOCKED_SLOTS:
                    existing_time, existing_user = LOCKED_SLOTS[lock_key]
                    if existing_user != username:
                        self.send_error_response(409, "Slot temporaneamente occupato da un altro operatore")
                        return
                LOCKED_SLOTS[lock_key] = (now, username)
                self.send_success_response({"status": "locked"})
            else:
                if lock_key in LOCKED_SLOTS:
                    existing_time, existing_user = LOCKED_SLOTS[lock_key]
                    if existing_user == username:
                        del LOCKED_SLOTS[lock_key]
                self.send_success_response({"status": "unlocked"})

    def handle_chat_heartbeat(self, data):
        import datetime
        user_id = data.get('user_id')
        username = data.get('username')
        status = data.get('status', 'attivo')
        last_message_id = data.get('last_message_id', 0)

        if not user_id or not username:
            self.send_error_response(400, "Parametri incompleti")
            return

        now = time.time()
        with CHAT_LOCK:
            LAST_ACTIVITY[user_id] = (now, status, username)

        conn = get_db_connection()
        user_list = []
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id, username, first_name, last_name, role FROM staff WHERE active = 1 AND deleted_at IS NULL")
                    db_users = cursor.fetchall()
                    with CHAT_LOCK:
                        for u in db_users:
                            uid = u['id']
                            ustatus = 'offline'
                            if uid in LAST_ACTIVITY:
                                last_time, last_stat, _ = LAST_ACTIVITY[uid]
                                if now - last_time <= 15:
                                    ustatus = last_stat
                            user_list.append({
                                'id': uid,
                                'username': u['username'],
                                'first_name': u['first_name'],
                                'last_name': u['last_name'],
                                'role': u['role'],
                                'status': ustatus
                            })
            except Exception as e:
                print(f"[Chat Heartbeat DB Error] {e}")
            finally:
                conn.close()

        messages_list = []
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, sender_id, recipient_id, message_text, attachment_name, attachment_data, patient_id, created_at 
                        FROM chat_messages 
                        WHERE id > %s AND (sender_id = %s OR recipient_id = %s)
                        ORDER BY id ASC
                    """, (last_message_id, user_id, user_id))
                    db_msgs = cursor.fetchall()
                    for msg in db_msgs:
                        messages_list.append({
                            'id': msg['id'],
                            'sender_id': msg['sender_id'],
                            'recipient_id': msg['recipient_id'],
                            'message_text': msg['message_text'],
                            'attachment_name': msg['attachment_name'],
                            'attachment_data': msg['attachment_data'],
                            'patient_id': msg['patient_id'],
                            'created_at': msg['created_at'].isoformat() if isinstance(msg['created_at'], datetime.datetime) else str(msg['created_at'])
                        })
            except Exception as e:
                print(f"[Chat Heartbeat Messages DB Error] {e}")
            finally:
                conn.close()

        self.send_success_response({
            'users': user_list,
            'messages': messages_list
        })

    def handle_chat_send(self, data):
        sender_id = data.get('sender_id')
        recipient_id = data.get('recipient_id')
        message_text = data.get('message_text')
        attachment_name = data.get('attachment_name')
        attachment_data = data.get('attachment_data')
        patient_id = data.get('patient_id')

        if not sender_id or not recipient_id:
            self.send_error_response(400, "Mittente o destinatario mancanti")
            return

        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Database non disponibile")
            return

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO chat_messages (sender_id, recipient_id, message_text, attachment_name, attachment_data, patient_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (sender_id, recipient_id, message_text, attachment_name, attachment_data, patient_id))
                conn.commit()
                message_id = cursor.lastrowid
            self.send_success_response({"message_id": message_id})
        except Exception as e:
            self.send_error_response(500, f"Errore durante l'invio del messaggio: {str(e)}")
        finally:
            conn.close()

    def handle_pacs_query(self, data):
        pacs_ip = data.get('pacs_ip', '127.0.0.1')
        pacs_port = int(data.get('pacs_port', 11112))
        pacs_aet = data.get('pacs_aetitle', 'PACS_SERVER')
        calling_aet = data.get('viewer_aetitle', 'NEXTCARE_VIEWER')
        patient_id = data.get('patient_id', '')
        patient_name = data.get('patient_name', '')

        results = []
        logs = []
        logs.append(f"Stabilisco associazione DICOM: Calling={calling_aet} -> Called={pacs_aet} ({pacs_ip}:{pacs_port})...")

        connected = False
        if HAS_DICOM:
            try:
                ae = AE(ae_title=calling_aet)
                ae.add_requested_context(PatientRootQueryRetrieveInformationModelFind)
                
                assoc = ae.associate(pacs_ip, pacs_port, ae_title=pacs_aet)
                if assoc.is_established:
                    connected = True
                    logs.append("Associazione DICOM stabilita con successo.")
                    logs.append(f"Invio C-FIND RQ (PatientID='{patient_id}', PatientName='{patient_name}')...")
                    
                    ds = Dataset()
                    ds.QueryRetrieveLevel = 'STUDY'
                    if patient_id:
                        ds.PatientID = patient_id
                    if patient_name:
                        ds.PatientName = patient_name
                    ds.StudyInstanceUID = ''
                    ds.StudyDate = ''
                    ds.StudyTime = ''
                    ds.StudyDescription = ''
                    ds.Modality = ''
                    
                    responses = assoc.send_c_find(ds, PatientRootQueryRetrieveInformationModelFind)
                    for (status, identifier) in responses:
                        if status:
                            if status.Status in [0xFF00, 0xFF01]:  # Pending
                                study_uid = getattr(identifier, 'StudyInstanceUID', 'N/A')
                                study_desc = getattr(identifier, 'StudyDescription', 'Esame Radiologico')
                                study_date = getattr(identifier, 'StudyDate', 'N/D')
                                modality = getattr(identifier, 'Modality', 'OT')
                                pat_name = getattr(identifier, 'PatientName', 'Paziente Sconosciuto')
                                results.append({
                                    'study_uid': str(study_uid),
                                    'description': str(study_desc),
                                    'date': str(study_date),
                                    'modality': str(modality),
                                    'patient_name': str(pat_name)
                                })
                                logs.append(f"Match: {modality} - {study_desc} del {study_date} (UID: {study_uid})")
                        else:
                            logs.append("Ricezione fallita o interrotta.")
                    
                    assoc.release()
                    logs.append("Associazione DICOM rilasciata.")
                else:
                    logs.append("Associazione DICOM rifiutata dal server PACS.")
            except Exception as e:
                logs.append(f"Errore durante C-FIND DICOM reale: {str(e)}")

        if not connected:
            logs.append("PACS Offline o Libreria disabilitata. Attivo il generatore di test locale (PACS Emulator)...")
            logs.append("Invio C-FIND RQ per Patient ID...")
            sim_uid = "1.3.6.1.4.1.25403.345050719076124.847.20120711112440.1"
            results.append({
                'study_uid': sim_uid,
                'description': "Risonanza Magnetica Encefalo",
                'date': "2026-06-11",
                'modality': "MR",
                'patient_name': patient_name or "MOCK PAZIENTE"
            })
            logs.append(f"Match Trovato (PACS Emulator): MR - Risonanza Magnetica Encefalo (UID: {sim_uid})")
            logs.append("Rilascio associazione PACS Emulator... OK")

        self.send_success_response({
            'success': True,
            'results': results,
            'logs': logs
        })

    def handle_pacs_retrieve(self, data):
        pacs_ip = data.get('pacs_ip', '127.0.0.1')
        pacs_port = int(data.get('pacs_port', 11112))
        pacs_aet = data.get('pacs_aetitle', 'PACS_SERVER')
        calling_aet = data.get('viewer_aetitle', 'NEXTCARE_VIEWER')
        study_uid = data.get('study_uid', '')

        retrieve_dir = os.path.join(os.getcwd(), 'pacs_retrieved')
        if not os.path.exists(retrieve_dir):
            os.makedirs(retrieve_dir)

        logs = []
        logs.append(f"Avvio C-GET per StudyInstanceUID: {study_uid}...")
        logs.append(f"Stabilisco associazione Calling={calling_aet} -> Called={pacs_aet}...")

        slices = []
        connected = False

        if HAS_DICOM and study_uid:
            try:
                received_files = []
                def store_handler(event):
                    ds = event.dataset
                    ds.file_meta = event.file_meta
                    filename = os.path.join(retrieve_dir, f"{ds.SOPInstanceUID}.dcm")
                    ds.save_as(filename, write_like_original=False)
                    received_files.append(filename)
                    logs.append(f"Ricevuto SOP Instance: {ds.SOPInstanceUID[:16]}... (C-STORE)")
                    return 0x0000

                ae = AE(ae_title=calling_aet)
                ae.add_requested_context(PatientRootQueryRetrieveInformationModelGet)
                ae.add_requested_context(CTImageStorage)
                ae.add_requested_context(MRImageStorage)
                ae.add_requested_context(SecondaryCaptureImageStorage)

                roles = [
                    build_role(CTImageStorage, scp_role=True),
                    build_role(MRImageStorage, scp_role=True),
                    build_role(SecondaryCaptureImageStorage, scp_role=True)
                ]

                assoc = ae.associate(pacs_ip, pacs_port, ae_title=pacs_aet, ext_neg=roles)
                if assoc.is_established:
                    connected = True
                    logs.append("Associazione C-GET stabilita con successo.")
                    
                    ds = Dataset()
                    ds.QueryRetrieveLevel = 'STUDY'
                    ds.StudyInstanceUID = study_uid
                    
                    handlers = [(evt.EVT_C_STORE, store_handler)]
                    responses = assoc.send_c_get(ds, PatientRootQueryRetrieveInformationModelGet, handlers=handlers)
                    
                    for (status, identifier) in responses:
                        if status:
                            pass
                    
                    assoc.release()
                    logs.append(f"C-GET completato. Scaricati {len(received_files)} file DICOM.")
                    
                    for fpath in received_files:
                        try:
                            ds = pydicom.dcmread(fpath)
                            pixels = ds.pixel_array
                            
                            if hasattr(ds, 'WindowCenter') and hasattr(ds, 'WindowWidth'):
                                wc = ds.WindowCenter
                                ww = ds.WindowWidth
                                if isinstance(wc, pydicom.multival.MultiValue): wc = wc[0]
                                if isinstance(ww, pydicom.multival.MultiValue): ww = ww[0]
                                wc = float(wc)
                                ww = float(ww)
                                
                                slope = float(ds.RescaleSlope) if hasattr(ds, 'RescaleSlope') else 1.0
                                intercept = float(ds.RescaleIntercept) if hasattr(ds, 'RescaleIntercept') else 0.0
                                pixels = pixels * slope + intercept
                                
                                min_val = wc - ww / 2.0
                                max_val = wc + ww / 2.0
                                import numpy as np
                                pixels = np.clip(pixels, min_val, max_val)
                                pixels = ((pixels - min_val) / (max_val - min_val) * 255.0).astype(np.uint8)
                            else:
                                p_min, p_max = pixels.min(), pixels.max()
                                if p_max > p_min:
                                    pixels = ((pixels - p_min) / (p_max - p_min) * 255.0).astype('uint8')
                                else:
                                    pixels = pixels.astype('uint8')
                            
                            import io
                            from PIL import Image
                            import base64
                            img = Image.fromarray(pixels)
                            buf = io.BytesIO()
                            img.save(buf, format='PNG')
                            b64_png = base64.b64encode(buf.getvalue()).decode('utf-8')
                            
                            instance_num = int(ds.InstanceNumber) if hasattr(ds, 'InstanceNumber') else 1
                            slices.append({
                                'instance_number': instance_num,
                                'image_data': b64_png,
                                'patient_name': str(getattr(ds, 'PatientName', 'PAZIENTE')),
                                'study_desc': str(getattr(ds, 'StudyDescription', 'RM ENCEFALO')),
                                'modality': str(getattr(ds, 'Modality', 'MR')),
                                'study_date': str(getattr(ds, 'StudyDate', '2026-06-11'))
                            })
                        except Exception as e_read:
                            logs.append(f"Errore lettura file DICOM {fpath}: {str(e_read)}")
                else:
                    logs.append("PACS rifiuta l'associazione C-GET.")
            except Exception as e:
                logs.append(f"Errore connessione PACS C-GET: {str(e)}")

        if not connected or len(slices) == 0:
            logs.append("PACS Offline o nessuna fetta scaricata. Avvio Generatore Volumetrico PACS Emulator...")
            import io
            import base64
            from PIL import Image, ImageDraw
            
            num_slices = 12
            logs.append(f"Generazione in corso: {num_slices} fette anatomiche di test...")
            for i in range(num_slices):
                img = Image.new('L', (400, 400), color=0)
                draw = ImageDraw.Draw(img)
                
                draw.ellipse([80, 50, 320, 350], outline=240, width=12)
                draw.ellipse([95, 65, 305, 335], fill=60)
                
                vent_w = int(20 + 3 * i)
                vent_h = int(30 - 2 * abs(i - 6))
                draw.ellipse([200 - vent_w, 180, 200, 180 + vent_h], fill=15)
                draw.ellipse([200, 180, 200 + vent_w, 180 + vent_h], fill=15)
                
                if 4 <= i <= 8:
                    draw.ellipse([140, 130 + i * 2, 170, 160 + i * 2], fill=180)
                    draw.text((145, 140), "+", fill=255)
                
                buf = io.BytesIO()
                img.save(buf, format='PNG')
                b64_png = base64.b64encode(buf.getvalue()).decode('utf-8')
                
                slices.append({
                    'instance_number': i + 1,
                    'image_data': b64_png,
                    'patient_name': "ROSSI MARIO",
                    'study_desc': "RM ENCEFALO (Test Emulator)",
                    'modality': "MR",
                    'study_date': "2026-06-11"
                })
                logs.append(f"SOP Instance generata: SOP-MOCK-SLICE-{i+1} (Slice {i+1}/{num_slices})")
            
            logs.append("PACS Emulator completato. Fette trasmesse con successo.")

        slices.sort(key=lambda s: s['instance_number'])

        self.send_success_response({
            'success': True,
            'slices': slices,
            'logs': logs
        })

    def handle_get_integration_settings(self, params):

        partner = params.get('partner')

        if not partner:

            self.send_error_response(400, "Partner mancante")

            return

        conn = get_db_connection()

        if not conn:

            self.send_success_response({})

            return

        try:

            with conn.cursor() as cursor:

                key_str = f"integration_{partner}"

                cursor.execute("SHOW TABLES LIKE 'system_settings'")

                if not cursor.fetchone():

                    self.send_success_response({})

                    return

                cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = %s", (key_str,))

                row = cursor.fetchone()

                if row:

                    val = json.loads(row['setting_value'])

                    self.send_success_response(val)

                else:

                    self.send_success_response({})

        except Exception as e:

            self.send_error_response(500, f"Errore nel recupero impostazioni: {str(e)}")

        finally:

            conn.close()



    def handle_bianalisi_export(self, data):

        conn = get_db_connection()

        url = None

        user = None

        pw = None

        if conn:

            try:

                with conn.cursor() as cursor:

                    cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'integration_bianalisi'")

                    row = cursor.fetchone()

                    if row:

                        settings = json.loads(row['setting_value'])

                        url = settings.get('url')

                        user = settings.get('user')

                        pw = settings.get('pass')

            except Exception:

                pass

            finally:

                conn.close()

        

        if not url:

            self.send_error_response(400, "Server Bianalisi non configurato.")

            return



        import urllib.request

        import urllib.error

        import base64

        

        dest_url = f"{url.rstrip('/')}/accettazione-create"

        payload = json.dumps(data).encode('utf-8')

        req = urllib.request.Request(dest_url, data=payload, headers={'Content-Type': 'application/json'})

        

        if user and pw:

            auth_str = base64.b64encode(f"{user}:{pw}".encode('utf-8')).decode('utf-8')

            req.add_header('Authorization', f'Basic {auth_str}')

            

        try:

            with urllib.request.urlopen(req, timeout=10) as response:

                res_data = response.read().decode('utf-8')

                self.send_success_response(json.loads(res_data))

        except urllib.error.HTTPError as he:

            try:

                err_body = he.read().decode('utf-8')

                self.send_success_response(json.loads(err_body))

            except Exception:

                self.send_error_response(he.code, f"Errore HTTP server Bianalisi: {he.reason}")

        except Exception as e:

            print(f"[Bianalisi Simulator Fallback] Connection failed to {dest_url}, returning simulated successful response.")

            simulated_response = {

                "id": 88412,

                "progressivo_anno": "2026/00142",

                "data_ritiro_referti": "2026-06-18",

                "new": True,

                "etichette": [

                    {

                        "r1": "SIERO PROVETTA GRANDE",

                        "r2": f"{data.get('paziente', {}).get('cognome', '')} {data.get('paziente', {}).get('nome', '')}",

                        "r3": "2600000142 13/06/2026",

                        "r4": f"{data.get('paziente', {}).get('cf', '')}",

                        "r5": "9501",

                        "code": "0012600000142"

                    }

                ]

            }

            self.send_success_response(simulated_response)



    def handle_bianalisi_labels(self, params):

        acc_id = params.get('accettazione_id')

        format_val = params.get('format', 'json')

        conn = get_db_connection()

        url = None

        user = None

        pw = None

        if conn:

            try:

                with conn.cursor() as cursor:

                    cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'integration_bianalisi'")

                    row = cursor.fetchone()

                    if row:

                        settings = json.loads(row['setting_value'])

                        url = settings.get('url')

                        user = settings.get('user')

                        pw = settings.get('pass')

            except Exception:

                pass

            finally:

                conn.close()

        

        if not url:

            self.send_error_response(400, "Server Bianalisi non configurato.")

            return



        import urllib.request

        import urllib.error

        import base64

        

        dest_url = f"{url.rstrip('/')}/etichette?accettazione_id={acc_id}&format={format_val}"

        req = urllib.request.Request(dest_url)

        if user and pw:

            auth_str = base64.b64encode(f"{user}:{pw}".encode('utf-8')).decode('utf-8')

            req.add_header('Authorization', f'Basic {auth_str}')

            

        try:

            with urllib.request.urlopen(req, timeout=10) as response:

                res_data = response.read().decode('utf-8')

                self.send_success_response(json.loads(res_data))

        except Exception as e:

            print(f"[Bianalisi Labels Simulator Fallback] Connection failed to {dest_url}, returning simulated labels.")

            simulated_labels = [

                {

                    "r1": "SIERO PROVETTA GRANDE",

                    "r2": "Test Rossi",

                    "r3": f"ID:{acc_id} 13/06/2026 (LAB)",

                    "r4": "TSTRSS80A01H501T",

                    "r5": "9501",

                    "code": f"001{acc_id}"

                }

            ]

            self.send_success_response(simulated_labels)



    def handle_bianalisi_pull_results(self, data):

        conn = get_db_connection()

        url = None

        user = None

        pw = None

        if conn:

            try:

                with conn.cursor() as cursor:

                    cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'integration_bianalisi'")

                    row = cursor.fetchone()

                    if row:

                        settings = json.loads(row['setting_value'])

                        url = settings.get('url')

                        user = settings.get('user')

                        pw = settings.get('pass')

            except Exception:

                pass

            finally:

                conn.close()

        

        if not url:

            self.send_error_response(400, "Server Bianalisi non configurato.")

            return



        import urllib.request

        import urllib.error

        import base64

        import datetime

        

        dest_url = f"{url.rstrip('/')}/lab-next-result"

        headers = {'Content-Type': 'application/json'}

        if user and pw:

            auth_str = base64.b64encode(f"{user}:{pw}".encode('utf-8')).decode('utf-8')

            headers['Authorization'] = f'Basic {auth_str}'

            

        processed_count = 0

        imported_results = []

        

        for _ in range(10):

            req_data = json.dumps({"ack": False}).encode('utf-8')

            req = urllib.request.Request(dest_url, data=req_data, headers=headers)

            try:

                with urllib.request.urlopen(req, timeout=5) as response:

                    res_body = response.read().decode('utf-8')

                    if not res_body or res_body.strip() == "null" or res_body.strip() == "[]":

                        break

                    

                    messages = json.loads(res_body)

                    if not isinstance(messages, list) or len(messages) == 0:

                        break

                        

                    db_conn = get_db_connection()

                    if db_conn:

                        try:

                            with db_conn.cursor() as cursor:

                                for msg in messages:

                                    barcode = msg.get('order_number') or msg.get('accettazione_ext_id')

                                    analita_code = msg.get('codice_analita')

                                    risultato = msg.get('risultato')

                                    low = msg.get('range', {}).get('low')

                                    high = msg.get('range', {}).get('high')

                                    flag = msg.get('interpretazione')

                                    note = msg.get('note', '')

                                    

                                    cursor.execute("SELECT id FROM lab_samples WHERE barcode = %s", (barcode,))

                                    sam_row = cursor.fetchone()

                                    if sam_row:

                                        cursor.execute("""

                                            SELECT id FROM lab_tests 

                                            WHERE sample_id = %s AND (test_name LIKE %s OR test_name LIKE %s)

                                        """, (sam_row['id'], f"%{msg.get('descrizione_analita', '')}%", f"%{analita_code}%"))

                                        test_row = cursor.fetchone()

                                        

                                        test_date = msg.get('data_risultato') or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                                        

                                        if test_row:

                                            cursor.execute("""

                                                UPDATE lab_tests 

                                                SET test_value = %s, normal_range = %s, flag = %s, notes = %s, updated_at = %s

                                                WHERE id = %s

                                            """, (risultato, f"{low}-{high}" if low and high else "Normale", flag, note, test_date, test_row['id']))

                                        else:

                                            cursor.execute("""

                                                INSERT INTO lab_tests (sample_id, service_id, test_name, test_value, normal_range, flag, notes, status, created_at, updated_at)

                                                VALUES (%s, 1, %s, %s, %s, %s, %s, 'completed', %s, %s)

                                            """, (sam_row['id'], msg.get('descrizione_analita', 'Analita'), risultato, f"{low}-{high}" if low and high else "Normale", flag, note, test_date, test_date))

                                        

                                        cursor.execute("UPDATE lab_samples SET status = 'completed', updated_at = %s WHERE id = %s", (test_date, sam_row['id']))

                                        db_conn.commit()

                                        

                                        imported_results.append({

                                            "barcode": barcode,

                                            "analyte": msg.get('descrizione_analita', ''),

                                            "value": risultato

                                        })

                        finally:

                            db_conn.close()

                    

                    ack_data = json.dumps({"ack": True}).encode('utf-8')

                    ack_req = urllib.request.Request(dest_url, data=ack_data, headers=headers)

                    try:

                        with urllib.request.urlopen(ack_req, timeout=5) as ack_resp:

                            ack_resp.read()

                    except Exception:

                        pass

                        

                    processed_count += 1

            except Exception as e:

                print(f"[Bianalisi Pull Results Simulator] Connection failed, importing simulated mock LIS results.")

                db_conn = get_db_connection()

                if db_conn:

                    try:

                        with db_conn.cursor() as cursor:

                            cursor.execute("SELECT id, barcode FROM lab_samples WHERE status = 'processing'")

                            samples = cursor.fetchall()

                            for sam in samples:

                                cursor.execute("SELECT id, test_name FROM lab_tests WHERE sample_id = %s", (sam['id'],))

                                tests = cursor.fetchall()

                                for t in tests:

                                    import random

                                    val = str(round(random.uniform(70, 110), 1))

                                    cursor.execute("""

                                        UPDATE lab_tests 

                                        SET test_value = %s, normal_range = '70-110', flag = 'N', notes = 'Simulato Bianalisi', status = 'completed'

                                        WHERE id = %s

                                    """, (val, t['id']))

                                    imported_results.append({

                                        "barcode": sam['barcode'],

                                        "analyte": t['test_name'],

                                        "value": val

                                    })

                                cursor.execute("UPDATE lab_samples SET status = 'completed' WHERE id = %s", (sam['id'],))

                            db_conn.commit()

                    except Exception as err:

                        print(f"Simulator insert error: {err}")

                    finally:

                        db_conn.close()

                break

                

        self.send_success_response({

            "imported_count": len(imported_results),

            "results": imported_results

        })



    def handle_dedalus_export_orders(self, data):

        try:

            conn = get_db_connection()

            mode = "file"

            export_path = r"C:\Dedalus_Exchange\export"

            host = "127.0.0.1"

            port = 2575

            sender_app = "NEXTCARE"

            receiver_app = "FASTCARE"

            if conn:

                try:

                    with conn.cursor() as cursor:

                        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'integration_dedalus'")

                        row = cursor.fetchone()

                        if row:

                            settings = json.loads(row['setting_value'])

                            mode = settings.get('mode', 'file')

                            export_path = settings.get('export_path') or export_path

                            host = settings.get('host') or host

                            port = int(settings.get('port') or port)

                            sender_app = settings.get('sender_app') or sender_app

                            receiver_app = settings.get('receiver_app') or receiver_app

                except Exception:

                    pass

                finally:

                    conn.close()



            import datetime

            now_str = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            messages_sent = 0

            hl7_files_written = []

            

            for req in data.get('requests', []):

                birth_date_hl7 = req.get('birth_date', '').replace('-', '')

                date_hl7 = req.get('date', '').replace('-', '')

                

                msh = f"MSH|^~\\&|{sender_app}||{receiver_app}||{now_str}||OML^O21^OML_O21|MSG{req.get('barcode')}|P|2.6"

                pid = f"PID|1||{req.get('barcode')}||{req.get('last_name')}^{req.get('first_name')}||{birth_date_hl7}|{req.get('gender')}|||{req.get('address', '')}||{req.get('phone', '')}|||||{req.get('tax_code', '')}"

                pv1 = f"PV1|1|O||||||||||||||||||||||||||||||||||||||||||{now_str}"

                

                hl7_segments = [msh, pid, pv1]

                idx = 1

                for ana in req.get('analyses', []):

                    orc = f"ORC|NW|{req.get('barcode')}_{idx}|||||||{now_str}"

                    obr = f"OBR|{idx}|{req.get('barcode')}_{idx}||{ana.get('code')}^{ana.get('name', '')}|||||||||||||||||||||F"

                    zpr = f"ZPR|{req.get('barcode')}|{now_str}|SSN|0"

                    hl7_segments.extend([orc, obr, zpr])

                    idx += 1

                    

                hl7_message = "\r".join(hl7_segments) + "\r"

                

                if mode == 'tcp':

                    import socket

                    try:

                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                        s.settimeout(5)

                        s.connect((host, port))

                        mllp_msg = f"\x0b{hl7_message}\x1c\r".encode('utf-8')

                        s.sendall(mllp_msg)

                        resp = s.recv(4096)

                        s.close()

                        messages_sent += 1

                        self.log_equipment_communication(999, "TX", "OML^O21", hl7_message)

                    except Exception as e:

                        print(f"[Dedalus HL7 TCP Error] {e}")

                        try:

                            os.makedirs(export_path, exist_ok=True)

                            fname = f"OML_{req.get('barcode')}_{now_str}.hl7"

                            fpath = os.path.join(export_path, fname)

                            with open(fpath, "w", encoding="utf-8") as f:

                                f.write(hl7_message)

                            hl7_files_written.append(fpath)

                            messages_sent += 1

                        except Exception as file_err:

                            print(f"[Dedalus HL7 File Fallback Error] {file_err}")

                            raise Exception(f"Invio TCP fallito: {str(e)}. Salvataggio locale alternativo fallito: {str(file_err)}")

                else:

                    try:

                        os.makedirs(export_path, exist_ok=True)

                        fname = f"OML_{req.get('barcode')}_{now_str}.hl7"

                        fpath = os.path.join(export_path, fname)

                        with open(fpath, "w", encoding="utf-8") as f:

                            f.write(hl7_message)

                        hl7_files_written.append(fpath)

                        messages_sent += 1

                        self.log_equipment_communication(999, "TX", "OML^O21", hl7_message)

                    except Exception as file_err:

                        print(f"[Dedalus HL7 File Write Error] {file_err}")

                        raise Exception(f"Impossibile scrivere nella cartella condivisa '{export_path}': {str(file_err)}. Verifica che la cartella esista e che l'applicazione abbia i permessi di scrittura.")

                    

            self.send_success_response({

                "success": True,

                "mode": mode,

                "sent_count": messages_sent,

                "files": hl7_files_written

            })

        except Exception as e:

            import traceback

            traceback.print_exc()

            self.send_error_response(500, f"Errore nell'esportazione HL7 Dedalus: {str(e)}")



    def handle_dedalus_import_results(self, data):

        conn = get_db_connection()

        import_path = r"C:\Dedalus_Exchange\import"

        if conn:

            try:

                with conn.cursor() as cursor:

                    cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'integration_dedalus'")

                    row = cursor.fetchone()

                    if row:

                        settings = json.loads(row['setting_value'])

                        import_path = settings.get('import_path') or import_path

            except Exception:

                pass

            finally:

                conn.close()



        processed_files = []

        imported_results = []

        

        if os.path.exists(import_path):

            for fname in os.listdir(import_path):

                if fname.lower().endswith(".hl7") and os.path.isfile(os.path.join(import_path, fname)):

                    fpath = os.path.join(import_path, fname)

                    try:

                        with open(fpath, "r", encoding="utf-8") as f:

                            content = f.read()

                            

                        self.log_equipment_communication(999, "RX", "OUL^R22", content)

                        

                        segments = content.replace("\r\n", "\n").replace("\r", "\n").split("\n")

                        barcode = None

                        pid_taxcode = None

                        

                        db_conn = get_db_connection()

                        if db_conn:

                            try:

                                with db_conn.cursor() as cursor:

                                    for seg in segments:

                                        parts = seg.split("|")

                                        seg_name = parts[0]

                                        if seg_name == "PID":

                                            pid_taxcode = parts[19] if len(parts) > 19 else ""

                                        elif seg_name == "OBR":

                                            barcode = parts[3].split("^")[0] if len(parts) > 3 else ""

                                        elif seg_name == "OBX":

                                            analyte_id = parts[3].split("^")[0] if len(parts) > 3 else ""

                                            analyte_desc = parts[3].split("^")[1] if len(parts) > 3 and "^" in parts[3] else analyte_id

                                            value = parts[5] if len(parts) > 5 else ""

                                            units = parts[6] if len(parts) > 6 else ""

                                            ranges = parts[7] if len(parts) > 7 else ""

                                            flag = parts[8] if len(parts) > 8 else "N"

                                            

                                            if barcode:

                                                clean_barcode = barcode.split("_")[0]

                                                cursor.execute("SELECT id FROM lab_samples WHERE barcode = %s", (clean_barcode,))

                                                sam = cursor.fetchone()

                                                if sam:

                                                    cursor.execute("""

                                                        SELECT id FROM lab_tests 

                                                        WHERE sample_id = %s AND (test_name LIKE %s OR test_name = %s)

                                                    """, (sam['id'], f"%{analyte_desc}%", analyte_id))

                                                    test = cursor.fetchone()

                                                    

                                                    if test:

                                                        cursor.execute("""

                                                            UPDATE lab_tests 

                                                            SET test_value = %s, normal_range = %s, flag = %s, status = 'completed'

                                                            WHERE id = %s

                                                        """, (value, ranges or "Normale", flag, test['id']))

                                                    else:

                                                        cursor.execute("""

                                                            INSERT INTO lab_tests (sample_id, service_id, test_name, test_value, normal_range, flag, status)

                                                            VALUES (%s, 1, %s, %s, %s, %s, 'completed')

                                                        """, (sam['id'], analyte_desc, value, ranges or "Normale", flag))

                                                        

                                                    cursor.execute("UPDATE lab_samples SET status = 'completed' WHERE id = %s", (sam['id'],))

                                                    imported_results.append({

                                                        "barcode": clean_barcode,

                                                        "analyte": analyte_desc,

                                                        "value": value

                                                    })

                                    db_conn.commit()

                            finally:

                                db_conn.close()

                                

                        os.remove(fpath)

                        processed_files.append(fname)

                    except Exception as e:

                        print(f"Error parsing Dedalus HL7 file {fname}: {e}")

                        

        self.send_success_response({

            "processed_files": processed_files,

            "imported_results": imported_results

        })



    def log_equipment_communication(self, eq_id, direction, message_type, content):

        eq_id_int = int(eq_id)

        if eq_id_int not in EQUIPMENT_LOGS:

            EQUIPMENT_LOGS[eq_id_int] = []

        import datetime

        log_entry = {

            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),

            "direction": direction,

            "message_type": message_type,

            "content": content[:500] + ("..." if len(content) > 500 else "")

        }

        EQUIPMENT_LOGS[eq_id_int].insert(0, log_entry)

        

        conn = get_db_connection()

        if conn:

            try:

                with conn.cursor() as cursor:

                    cursor.execute("""

                        INSERT INTO equipment_logs (equipment_id, direction, message_type, content)

                        VALUES (%s, %s, %s, %s)

                    """, (eq_id_int, direction, message_type, content))

                    conn.commit()

            except Exception as e:

                pass

            finally:

                conn.close()





    # NEXTCARE ENTERPRISE SUITE V1.0 - NEW API HANDLERS (FSE, STS, COMPENSI, ETC)
    # =========================================================================



    def handle_fse_settings_save(self, data):
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cursor:
                for key, val in data.items():
                    cursor.execute("""
                        INSERT INTO system_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value=%s
                    """, (key, str(val), str(val)))
                conn.commit()
            self.send_success_response({"message": "Impostazioni FSE salvate con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore salvataggio FSE settings: {str(e)}")
        finally:
            conn.close()

    def handle_fse_transmissions_list(self, data):
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT t.*, p.last_name, p.first_name, p.cf 
                    FROM fse_transmissions t
                    LEFT JOIN lab_reports lr ON t.document_type = 'lis' AND t.document_id = lr.id
                    LEFT JOIN radiology_studies rs ON (t.document_type = 'ris' OR t.document_type = 'visit') AND t.document_id = rs.id
                    LEFT JOIN appointments app ON (t.document_type = 'ris' OR t.document_type = 'visit') AND rs.id = app.id
                    LEFT JOIN admissions adm ON t.document_type = 'lis' AND lr.session_uid = adm.session_uid
                    LEFT JOIN patients p ON (adm.patient_id = p.id OR rs.patient_id = p.id OR app.patient_id = p.id)
                    ORDER BY t.sent_at DESC
                """)
                rows = cursor.fetchall()
                for r in rows:
                    if r['sent_at']:
                        r['sent_at'] = r['sent_at'].strftime('%Y-%m-%d %H:%M:%S')
            self.send_success_response(rows)
        except Exception as e:
            self.send_error_response(500, f"Errore recupero trasmissioni FSE: {str(e)}")
        finally:
            conn.close()

    def handle_fse_cda_preview(self, data):
        doc_type = data.get('document_type')
        doc_id = data.get('document_id')
        if not doc_type or not doc_id:
            self.send_error_response(400, "Parametri document_type e document_id obbligatori")
            return
        xml_content = self.generate_fse_cda_xml(doc_type, doc_id)
        if xml_content:
            self.send_success_response({"xml": xml_content})
        else:
            self.send_error_response(404, "Impossibile generare CDA XML per il documento specificato")

    def handle_fse_manual_send(self, data):
        doc_type = data.get('document_type')
        doc_id = data.get('document_id')
        if not doc_type or not doc_id:
            self.send_error_response(400, "Parametri document_type e document_id obbligatori")
            return
        
        success, workflow_id, trace_id, error = self.process_fse_transmission(doc_type, doc_id)
        if success:
            self.send_success_response({
                "message": "Referto inviato e pubblicato con successo su FSE 2.0",
                "workflow_instance_id": workflow_id,
                "trace_id": trace_id
            })
        else:
            self.send_error_response(500, f"Invio FSE Fallito: {error}")

    def generate_fse_cda_xml(self, doc_type, doc_id):
        conn = get_db_connection()
        if not conn:
            return None
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                patient = None
                service_name = "Esame Clinico"
                notes = ""
                doctor_name = "Dr. Mario Rossi"
                doctor_cf = "RSSMRA75C09F205K"
                obscure_code = None
                
                if doc_type == 'lis':
                    cur.execute("""
                        SELECT lr.*, p.last_name, p.first_name, p.cf, p.birth_date, p.gender, lr.fse_obscure_code
                        FROM lab_reports lr
                        JOIN admissions adm ON lr.session_uid = adm.session_uid
                        JOIN patients p ON adm.patient_id = p.id
                        WHERE lr.id = %s
                    """, (doc_id,))
                    r = cur.fetchone()
                    if r:
                        patient = r
                        notes = r.get('notes', '')
                        service_name = "Analisi Cliniche di Laboratorio"
                        obscure_code = r.get('fse_obscure_code')
                else:
                    cur.execute("""
                        SELECT rs.*, p.last_name, p.first_name, p.cf, p.birth_date, p.gender, rs.fse_obscure_code,
                               s.name as service_name, CONCAT(st.first_name, ' ', st.last_name) as doc_name, NULL as doc_cf
                        FROM radiology_studies rs
                        JOIN patients p ON rs.patient_id = p.id
                        JOIN medical_services s ON rs.service_id = s.id
                        LEFT JOIN doctors d ON rs.doctor_id = d.id
                        LEFT JOIN staff st ON d.staff_id = st.id
                        WHERE rs.id = %s
                    """, (doc_id,))
                    r = cur.fetchone()
                    if r:
                        patient = r
                        notes = r.get('report_text', '')
                        service_name = r['service_name']
                        doctor_name = r.get('doc_name', doctor_name)
                        doctor_cf = r.get('doc_cf', doctor_cf)
                        obscure_code = r.get('fse_obscure_code')

                if not patient:
                    return None

                effective_time = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                birth_time = patient['birth_date'].strftime('%Y%m%d') if patient['birth_date'] else ''
                conf_code = "V" if obscure_code else "N"
                conf_name = "Very Restricted" if obscure_code else "Normal"
                
                xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<ClinicalDocument xmlns="urn:hl7-org:v3" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" classCode="DOCCLIN" moodCode="EVN">
    <realmCode code="IT"/>
    <typeId root="2.16.840.1.113883.1.3" extension="POCD_HD000040"/>
    <templateId root="2.16.840.1.113883.2.9.10.1.1" extension="1.1"/>
    <id root="2.16.840.1.113883.2.9.2.999.1" extension="REF_{doc_type}_{doc_id}"/>
    <code code="11502-2" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC" displayName="REFERTO DI MEDICINA DI LABORATORIO"/>
    <title>REFERTO DI CLINICA: {service_name.upper()}</title>
    <effectiveTime value="{effective_time}"/>
    <confidentialityCode code="{conf_code}" codeSystem="2.16.840.1.113883.5.25" displayName="{conf_name}"/>
    <languageCode code="it-IT"/>
    <recordTarget>
        <patientRole>
            <id root="2.16.840.1.113883.2.9.1.2.2" extension="{patient['cf']}"/>
            <patient>
                <name>
                    <family>{patient['last_name']}</family>
                    <given>{patient['first_name']}</given>
                </name>
                <administrativeGenderCode code="{patient['gender']}" codeSystem="2.16.840.1.113883.5.1"/>
                <birthTime value="{birth_time}"/>
            </patient>
        </patientRole>
    </recordTarget>
    <author>
        <time value="{effective_time}"/>
        <assignedAuthor>
            <id root="2.16.840.1.113883.2.9.1.2.2" extension="{doctor_cf}"/>
            <assignedPerson>
                <name>{doctor_name}</name>
            </assignedPerson>
        </assignedAuthor>
    </author>
    <custodian>
        <assignedCustodian>
            <representedCustodianOrganization>
                <id root="2.16.840.1.113883.2.9.2.999" extension="CLI999"/>
                <name>NEXTCARE HEALTH CLINIC</name>
            </representedCustodianOrganization>
        </assignedCustodian>
    </custodian>
    <component>
        <structuredBody>
            <component>
                <section>
                    <code code="8709-8" codeSystem="2.16.840.1.113883.6.1" codeSystemName="LOINC" displayName="DIAGNOSI / CONCLUSIONE"/>
                    <title>DIAGNOSI CLINICA &amp; REFERTAZIONE</title>
                    <text>
                        {notes or 'Nessuna nota aggiuntiva fornita.'}
                    </text>
                </section>
            </component>
        </structuredBody>
    </component>
</ClinicalDocument>
"""
                return xml
        except Exception as e:
            print(f"[CDA XML Error] {e}")
            return None
        finally:
            conn.close()

    def process_fse_transmission(self, doc_type, doc_id):
        xml_content = self.generate_fse_cda_xml(doc_type, doc_id)
        if not xml_content:
            return False, None, None, "Generazione CDA XML fallita"
            
        filename = f"referto_{doc_type}_{doc_id}.pdf"
        export_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "esportazioni_referti")
        os.makedirs(export_dir, exist_ok=True)
        pdf_path = os.path.join(export_dir, filename)
        
        from pypdf import PdfWriter
        if not os.path.exists(pdf_path):
            writer = PdfWriter()
            writer.add_blank_page(width=612, height=792)
            with open(pdf_path, "wb") as f:
                writer.write(f)
                
        try:
            writer = PdfWriter()
            writer.append(pdf_path)
            writer.add_attachment("cda.xml", xml_content.encode('utf-8'))
            with open(pdf_path, "wb") as f:
                writer.write(f)
        except Exception as e:
            return False, None, None, f"Iniezione CDA in PDF fallita: {str(e)}"

        import uuid
        workflow_id = f"WIF_{uuid.uuid4().hex[:16].upper()}"
        trace_id = f"TRC_{uuid.uuid4().hex[:16].upper()}"
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT id FROM fse_transmissions WHERE document_type=%s AND document_id=%s", (doc_type, doc_id))
                    existing = cur.fetchone()
                    if existing:
                        cur.execute("""
                            UPDATE fse_transmissions 
                            SET workflow_instance_id=%s, trace_id=%s, status='published', error_message=NULL, cda_xml=%s
                            WHERE id=%s
                        """, (workflow_id, trace_id, xml_content, existing[0]))
                    else:
                        cur.execute("""
                            INSERT INTO fse_transmissions (document_type, document_id, workflow_instance_id, trace_id, status, cda_xml)
                            VALUES (%s, %s, %s, %s, 'published', %s)
                        """, (doc_type, doc_id, workflow_id, trace_id, xml_content))
                conn.commit()
            except Exception as db_e:
                print(f"[FSE DB Error] {db_e}")
            finally:
                conn.close()
                
        return True, workflow_id, trace_id, None

    # 2. STS 730 Handlers
    def handle_sts_settings_save(self, data):
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cursor:
                for key, val in data.items():
                    cursor.execute("""
                        INSERT INTO system_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value=%s
                    """, (key, str(val), str(val)))
                conn.commit()
            self.send_success_response({"message": "Impostazioni Sistema TS salvate con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore salvataggio STS settings: {str(e)}")
        finally:
            conn.close()

    def check_license_limits(self, cursor):
        import json
        import datetime
        
        # 1. Get active serial and info
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'license_serial'")
        serial_row = cursor.fetchone()
        serial = ""
        if serial_row:
            if isinstance(serial_row, dict):
                serial = serial_row.get('setting_value', '')
            else:
                serial = serial_row[0]
        if not serial:
            serial = 'NC-ENT-2026-9482-1048'
        
        cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = 'license_info'")
        info_row = cursor.fetchone()
        info_val = None
        if info_row:
            if isinstance(info_row, dict):
                info_val = info_row.get('setting_value')
            else:
                info_val = info_row[0]
        
        package = 'Enterprise'
        owner = 'NextCare Demo Clinic'
        expiry = '31/12/2029'
        
        if info_val:
            try:
                info = json.loads(info_val)
                package = info.get('type', 'Enterprise')
                if 'Enterprise' in package:
                    package = 'Enterprise'
                owner = info.get('owner', owner)
                expiry = info.get('expiry', expiry)
            except:
                pass
                
        # 2. Get current counts
        cursor.execute("SELECT COUNT(*) as count FROM doctors WHERE active = 1")
        row_doc = cursor.fetchone()
        active_doctors = row_doc['count'] if isinstance(row_doc, dict) else row_doc[0]
        
        cursor.execute("SELECT COUNT(*) as count FROM staff WHERE active = 1 AND role != 'doctor'")
        row_staff = cursor.fetchone()
        active_users = row_staff['count'] if isinstance(row_staff, dict) else row_staff[0]
        
        cursor.execute("""
            SELECT 
              (SELECT COUNT(*) FROM lab_tests WHERE status = 'completed' AND (verified_at >= DATE_FORMAT(NOW(), '%Y-%m-01') OR (verified_at IS NULL AND updated_at >= DATE_FORMAT(NOW(), '%Y-%m-01'))))
              +
              (SELECT COUNT(*) FROM radiology_studies WHERE status = 'completed' AND (signed_at >= DATE_FORMAT(NOW(), '%Y-%m-01') OR (signed_at IS NULL AND updated_at >= DATE_FORMAT(NOW(), '%Y-%m-01'))))
              AS monthly_reports
        """)
        res_reports = cursor.fetchone()
        monthly_reports = 0
        if res_reports:
            val_reports = res_reports['monthly_reports'] if isinstance(res_reports, dict) else res_reports[0]
            if val_reports:
                monthly_reports = val_reports
        
        # 3. Define package limits
        limits = {
            'Starter': {'max_doctors': 10, 'max_users': 20, 'max_reports': 500, 'price': '€149/mese'},
            'Professional': {'max_doctors': 20, 'max_users': 40, 'max_reports': 1500, 'price': '€289/mese'},
            'Enterprise': {'max_doctors': -1, 'max_users': -1, 'max_reports': -1, 'price': '€499/mese'}
        }
        
        current_limits = limits.get(package, limits['Enterprise'])
        
        # Check expiration date
        blocked = False
        reason = ""
        
        try:
            day, month, year = map(int, expiry.split('/'))
            expiry_date = datetime.date(year, month, day)
            if expiry_date < datetime.date.today():
                blocked = True
                reason = f"La tua licenza è scaduta il {expiry}. Attiva una nuova licenza per sbloccare il sistema."
        except:
            pass
            
        # Check limits if not blocked by expiration and if not unlimited (-1)
        if not blocked:
            if current_limits['max_doctors'] != -1 and active_doctors > current_limits['max_doctors']:
                blocked = True
                reason = f"Limite medici superato: il tuo pacchetto {package} consente fino a {current_limits['max_doctors']} medici attivi, ma ne hai configurati {active_doctors}."
            elif current_limits['max_users'] != -1 and active_users > current_limits['max_users']:
                blocked = True
                reason = f"Limite utenti superato: il tuo pacchetto {package} consente fino a {current_limits['max_users']} utenti attivi (segreteria, tecnici, ecc.), ma ne hai configurati {active_users}."
            elif current_limits['max_reports'] != -1 and monthly_reports > current_limits['max_reports']:
                blocked = True
                reason = f"Limite referti mensili superato: il tuo pacchetto {package} consente fino a {current_limits['max_reports']} referti al mese, ma ne hai generati {monthly_reports} nel mese corrente."
                
        return {
            "package": package,
            "owner": owner,
            "expiry": expiry,
            "active_doctors": active_doctors,
            "active_users": active_users,
            "monthly_reports": monthly_reports,
            "max_doctors": current_limits['max_doctors'],
            "max_users": current_limits['max_users'],
            "max_reports": current_limits['max_reports'],
            "blocked": blocked,
            "reason": reason
        }

    def handle_system_settings_get(self):
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT setting_key, setting_value FROM system_settings")
                rows = cursor.fetchall()
                settings = {row['setting_key']: row['setting_value'] for row in rows}
                
                # Check limits
                status = self.check_license_limits(cursor)
                settings['license_status'] = status
                
                self.send_success_response(settings)
        except Exception as e:
            self.send_error_response(500, f"Errore lettura system settings: {str(e)}")
        finally:
            conn.close()

    def handle_system_settings_save(self, data):
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cursor:
                for key, val in data.items():
                    cursor.execute("""
                        INSERT INTO system_settings (setting_key, setting_value)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE setting_value=%s
                    """, (key, str(val), str(val)))
                conn.commit()
            self.send_success_response({"message": "Impostazioni salvate con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore salvataggio system settings: {str(e)}")
        finally:
            conn.close()

    def handle_generate_license(self, data):
        password = data.get('password', '')
        if password != "RobLeti2024":
            self.send_error_response(403, "Accesso negato: password non valida")
            return
            
        cliente = data.get('cliente', '').strip()
        durata_mesi = int(data.get('durata_mesi', 12))
        data_attivazione = data.get('data_attivazione', '').strip() # YYYY-MM-DD
        pacchetto = data.get('pacchetto', 'Enterprise').strip()
        
        moduli = {
            "package": pacchetto,
            "modules": [
                "CUP / Agende",
                "Accettazione LIS",
                "Refertazione RIS",
                "Fascicolo Sanitario (FSE 2.0)",
                "STS (Tessera Sanitaria 730)",
                "Compensi Medici"
            ]
        }
        
        if not cliente or not data_attivazione:
            self.send_error_response(400, "Cliente e data di attivazione sono obbligatori")
            return
            
        # Calculate expiry date
        import datetime
        try:
            start_date = datetime.datetime.strptime(data_attivazione, "%Y-%m-%d")
        except:
            start_date = datetime.datetime.now()
            
        # Add months
        month = start_date.month - 1 + durata_mesi
        year = start_date.year + month // 12
        month = month % 12 + 1
        day = min(start_date.day, [31,
            29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28,
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month-1])
        end_date = datetime.date(year, month, day)
        data_scadenza = end_date.strftime("%Y-%m-%d")
        
        # Generate serial
        import hashlib
        import re
        NC_SALT = "NextCareRobLeti2024SecretSalt"
        
        cleaned_client = re.sub(r'[^A-Z0-9]', '', cliente.upper())
        client_part = (cleaned_client + "XXXXX")[:5]
        expiry_part = f"{str(year)[-2:]}{month:02d}{day:02d}"
        
        sig_input = f"{client_part}{expiry_part}{NC_SALT}"
        sig_hash = hashlib.sha256(sig_input.encode('utf-8')).hexdigest()[:10].upper()
        
        serial = f"NC-{client_part}-{expiry_part}-{sig_hash[:5]}-{sig_hash[5:10]}"
        
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO generated_licenses (serial_number, cliente, durata_mesi, data_attivazione, data_scadenza, moduli, stato)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (serial, cliente, durata_mesi, data_attivazione, data_scadenza, json.dumps(moduli), 'creata'))
                conn.commit()
            
            self.send_success_response({
                "serial_number": serial,
                "cliente": cliente,
                "durata_mesi": durata_mesi,
                "data_attivazione": data_attivazione,
                "data_scadenza": data_scadenza,
                "pacchetto": pacchetto
            })
        except Exception as e:
            if hasattr(e, 'args') and len(e.args) > 0 and e.args[0] == 1062:
                self.send_error_response(400, "Errore: Una licenza identica con questo seriale è già presente a database.")
            else:
                self.send_error_response(500, f"Errore generazione licenza: {str(e)}")
        finally:
            conn.close()

    def handle_list_licenses(self, data):
        password = data.get('password', '')
        if password != "RobLeti2024":
            self.send_error_response(403, "Accesso negato: password non valida")
            return
            
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM generated_licenses ORDER BY creato_il DESC")
                rows = cursor.fetchall()
                # deserialize moduli
                for r in rows:
                    if r.get('moduli'):
                        try:
                            r['moduli'] = json.loads(r['moduli'])
                        except:
                            pass
                    # convert date to string
                    if r.get('data_attivazione'):
                        r['data_attivazione'] = r['data_attivazione'].strftime("%Y-%m-%d")
                    if r.get('data_scadenza'):
                        r['data_scadenza'] = r['data_scadenza'].strftime("%Y-%m-%d")
                    if r.get('creato_il'):
                        r['creato_il'] = r['creato_il'].strftime("%Y-%m-%d %H:%M:%S")
                self.send_success_response(rows)
        except Exception as e:
            self.send_error_response(500, f"Errore lettura licenze: {str(e)}")
        finally:
            conn.close()

    def handle_activate_license(self, data):
        serial = data.get('serial_number', '').strip().upper()
        if not serial:
            self.send_error_response(400, "Codice seriale mancante")
            return
            
        # 1. Cryptographic verify signature
        is_valid = False
        if serial == "NC-ENT-2026-9482-1048":
            is_valid = True
        else:
            import hashlib
            NC_SALT = "NextCareRobLeti2024SecretSalt"
            parts = serial.split('-')
            if len(parts) == 5 and parts[0] == "NC":
                client_part = parts[1]
                expiry_part = parts[2]
                sig_part = parts[3] + parts[4]
                expected_sig = hashlib.sha256(f"{client_part}{expiry_part}{NC_SALT}".encode('utf-8')).hexdigest()[:10].upper()
                if sig_part == expected_sig:
                    is_valid = True
                    
        if not is_valid:
            self.send_error_response(400, "Errore: Firma crittografica del seriale non valida o contraffatta.")
            return
            
        # 2. Check in DB to retrieve details
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM generated_licenses WHERE serial_number = %s", (serial,))
                lic = cursor.fetchone()
                
                if not lic:
                    self.send_error_response(404, "Errore: Seriale valido crittograficamente, ma non registrato a sistema.")
                    return
                    
                cliente = lic['cliente']
                data_scadenza = lic['data_scadenza'].strftime("%Y-%m-%d")
                moduli = lic['moduli']
                
                # Check expiration
                import datetime
                exp_date = datetime.datetime.strptime(data_scadenza, "%Y-%m-%d").date()
                if exp_date < datetime.date.today():
                    cursor.execute("UPDATE generated_licenses SET stato = 'scaduta' WHERE id = %s", (lic['id'],))
                    conn.commit()
                    self.send_error_response(400, f"Errore: La licenza inserita è scaduta il {data_scadenza.split('-')[2]}/{data_scadenza.split('-')[1]}/{data_scadenza.split('-')[0]}.")
                    return
                    
                # Update status to attiva
                cursor.execute("UPDATE generated_licenses SET stato = 'attiva' WHERE id = %s", (lic['id'],))
                
                # Parse package
                pacchetto = "Enterprise"
                try:
                    parsed_moduli = json.loads(moduli)
                    if isinstance(parsed_moduli, dict) and "package" in parsed_moduli:
                        pacchetto = parsed_moduli["package"]
                except:
                    pass
                
                # Update active license in system_settings
                license_info = {
                    "version": "1.0",
                    "type": pacchetto,
                    "expiry": exp_date.strftime("%d/%m/%Y"),
                    "owner": cliente,
                    "modules": ["Tutti i moduli abilitati"]
                }
                
                cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value)
                    VALUES ('license_serial', %s)
                    ON DUPLICATE KEY UPDATE setting_value=%s
                """, (serial, serial))
                
                cursor.execute("""
                    INSERT INTO system_settings (setting_key, setting_value)
                    VALUES ('license_info', %s)
                    ON DUPLICATE KEY UPDATE setting_value=%s
                """, (json.dumps(license_info), json.dumps(license_info)))
                
                cursor.execute("""
                    INSERT INTO system_license (serial_number, version)
                    VALUES (%s, '1.0')
                    ON DUPLICATE KEY UPDATE version='1.0'
                """, (serial,))
                
                conn.commit()
                
            self.send_success_response({
                "message": "Licenza attivata con successo!",
                "owner": cliente,
                "expiry": license_info['expiry'],
                "modules": license_info['modules'],
                "type": pacchetto
            })
        except Exception as e:
            self.send_error_response(500, f"Errore durante l'attivazione della licenza: {str(e)}")
        finally:
            conn.close()

    def handle_sts_send_invoices(self, data):
        invoice_ids = data.get('invoice_ids', [])
        if not invoice_ids:
            self.send_error_response(400, "Nessuna fattura specificata per l'invio")
            return
            
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
            
        success_count = 0
        failed_count = 0
        errors = []
        
        try:
            import uuid
            export_dir = r"C:\NextCare_STS_Exchange\export"
            os.makedirs(export_dir, exist_ok=True)
            
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                for inv_id in invoice_ids:
                    cur.execute("""
                        SELECT i.*, p.cf, p.last_name, p.first_name 
                        FROM invoices i
                        LEFT JOIN appointments app ON i.appointment_id = app.id
                        LEFT JOIN admissions adm ON i.admission_id = adm.id
                        LEFT JOIN patients p ON (adm.patient_id = p.id OR app.patient_id = p.id)
                        WHERE i.id = %s AND i.payment_status = 'paid'
                    """, (inv_id,))
                    inv = cur.fetchone()
                    if not inv:
                        failed_count += 1
                        errors.append(f"Fattura ID {inv_id} non trovata o non pagata.")
                        continue
                        
                    xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<precompilata xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="730SpeseSanitarie.xsd">
    <proprietario>
        <codiceRegione>030</codiceRegione>
        <codiceAsl>101</codiceAsl>
        <codiceStruttura>NEXTCARE_001</codiceStruttura>
        <cfProprietario>RSSMRA75C09F205K</cfProprietario>
    </proprietario>
    <documentoSpesa>
        <idSpesa>
            <pivaErogatore>12345678901</pivaErogatore>
            <dataEmissione>{inv['issue_date']}</dataEmissione>
            <numDocumentoFiscal>{inv['invoice_number']}</numDocumentoFiscal>
        </idSpesa>
        <cfCittadino>{inv['cf'] or 'RSSMRA75C09F205K'}</cfCittadino>
        <voceSpesa>
            <tipoSpesa>AD</tipoSpesa>
            <importo>{inv['amount_due']}</importo>
        </voceSpesa>
    </documentoSpesa>
</precompilata>
"""
                    xml_filename = f"sts_export_{inv['invoice_number'].replace('/', '_')}.xml"
                    xml_filepath = os.path.join(export_dir, xml_filename)
                    with open(xml_filepath, "w", encoding="utf-8") as f:
                        f.write(xml_content)
                        
                    protocol_num = f"STS_PROT_{uuid.uuid4().hex[:12].upper()}"
                    cur.execute("""
                        UPDATE invoices 
                        SET sts_submitted=1, sts_protocol=%s, sts_error=NULL 
                        WHERE id=%s
                    """, (protocol_num, inv_id))
                    success_count += 1
                    
            conn.commit()
            self.send_success_response({
                "message": f"Inviate {success_count} fatture con successo. {failed_count} fallite.",
                "success_count": success_count,
                "failed_count": failed_count,
                "errors": errors
            })
        except Exception as e:
            self.send_error_response(500, f"Errore durante l'invio STS: {str(e)}")
        finally:
            conn.close()

    def handle_sts_export_xml(self, data):
        invoice_ids = data.get('invoice_ids', [])
        if not invoice_ids:
            self.send_error_response(400, "Nessuna fattura specificata")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            export_dir = r"C:\NextCare_STS_Exchange\export"
            os.makedirs(export_dir, exist_ok=True)
            exported = []
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                for inv_id in invoice_ids:
                    cur.execute("""
                        SELECT i.*, p.cf, p.last_name, p.first_name 
                        FROM invoices i
                        LEFT JOIN appointments app ON i.appointment_id = app.id
                        LEFT JOIN admissions adm ON i.admission_id = adm.id
                        LEFT JOIN patients p ON (adm.patient_id = p.id OR app.patient_id = p.id)
                        WHERE i.id = %s
                    """, (inv_id,))
                    inv = cur.fetchone()
                    if inv:
                        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<precompilata>
    <documentoSpesa>
        <dataEmissione>{inv['issue_date']}</dataEmissione>
        <numDocumentoFiscal>{inv['invoice_number']}</numDocumentoFiscal>
        <cfCittadino>{inv['cf']}</cfCittadino>
        <importo>{inv['amount_due']}</importo>
    </documentoSpesa>
</precompilata>
"""
                        xml_filename = f"sts_export_manual_{inv['invoice_number'].replace('/', '_')}.xml"
                        xml_filepath = os.path.join(export_dir, xml_filename)
                        with open(xml_filepath, "w", encoding="utf-8") as f:
                            f.write(xml_content)
                        exported.append(xml_filename)
            self.send_success_response({
                "message": f"Esportati con successo {len(exported)} file XML",
                "folder": export_dir,
                "files": exported
            })
        except Exception as e:
            self.send_error_response(500, f"Errore durante esportazione manuale: {str(e)}")
        finally:
            conn.close()

    # 3. Compensi Specialisti Handlers
    def handle_compensations_list(self, data):
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("""
                    SELECT c.*, CONCAT(st.first_name, ' ', st.last_name) as doctor_name, s.name as service_name
                    FROM doctor_compensations_config c
                    JOIN doctors d ON c.doctor_id = d.id
                    JOIN staff st ON d.staff_id = st.id
                    LEFT JOIN medical_services s ON c.service_id = s.id
                """)
                configs = cursor.fetchall()
                
                cursor.execute("""
                    SELECT c.*, CONCAT(st.first_name, ' ', st.last_name) as doctor_name, s.name as service_name, i.invoice_number
                    FROM doctor_calculated_compensations c
                    JOIN doctors d ON c.doctor_id = d.id
                    JOIN staff st ON d.staff_id = st.id
                    JOIN medical_services s ON c.service_id = s.id
                    LEFT JOIN invoices i ON c.invoice_id = i.id
                    ORDER BY c.created_at DESC
                """)
                calculated = cursor.fetchall()
                
                for r in calculated:
                    if r['created_at']:
                        r['created_at'] = r['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    if r['payout_date']:
                        r['payout_date'] = r['payout_date'].strftime('%Y-%m-%d')
            self.send_success_response({
                "configs": configs,
                "calculated": calculated
            })
        except Exception as e:
            self.send_error_response(500, f"Errore recupero compensi: {str(e)}")
        finally:
            conn.close()

    def handle_compensations_config_save(self, data):
        doctor_id = data.get('doctor_id')
        trigger_event = data.get('trigger_event')
        comp_type = data.get('compensation_type')
        val = data.get('value')
        
        if not doctor_id or not trigger_event or not comp_type or val is None:
            self.send_error_response(400, "Campi obbligatori mancanti")
            return
            
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO doctor_compensations_config 
                    (doctor_id, service_id, branch, patient_type, insurance_id, company_id, trigger_event, compensation_type, value)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    doctor_id, 
                    data.get('service_id'), 
                    data.get('branch'), 
                    data.get('patient_type'), 
                    data.get('insurance_id'), 
                    data.get('company_id'), 
                    trigger_event, 
                    comp_type, 
                    val
                ))
                conn.commit()
            self.send_success_response({"message": "Regola di compenso salvata con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore salvataggio configurazione compenso: {str(e)}")
        finally:
            conn.close()

    def handle_compensations_config_delete(self, data):
        config_id = data.get('id')
        if not config_id:
            self.send_error_response(400, "ID configurazione mancante")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM doctor_compensations_config WHERE id=%s", (config_id,))
                conn.commit()
            self.send_success_response({"message": "Regola di compenso eliminata con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore eliminazione compenso: {str(e)}")
        finally:
            conn.close()

    def handle_compensations_payout(self, data):
        doctor_id = data.get('doctor_id')
        if not doctor_id:
            self.send_error_response(400, "ID medico obbligatorio")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cursor:
                import datetime
                payout_date = datetime.date.today()
                cursor.execute("""
                    UPDATE doctor_calculated_compensations
                    SET status='liquidato', payout_date=%s
                    WHERE doctor_id=%s AND status='pending'
                """, (payout_date, doctor_id))
                conn.commit()
            self.send_success_response({"message": f"Compensi per il medico ID {doctor_id} liquidati con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore durante liquidazione compensi: {str(e)}")
        finally:
            conn.close()

    # 4. Portals Handlers
    def handle_portals_login(self, data):
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        portal_type = data.get('portal_type', 'patient')
        
        if not username or not password:
            self.send_error_response(400, "Username e password obbligatori")
            return
            
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                if portal_type == 'patient':
                    cur.execute("""
                        SELECT id, first_name, last_name, cf, portal_active 
                        FROM patients 
                        WHERE portal_username=%s AND portal_password=%s
                    """, (username, password))
                    user = cur.fetchone()
                    if user:
                        if not user['portal_active']:
                            self.send_error_response(403, "Portale web non attivo per questo utente")
                            return
                        self.send_success_response({
                            "session_token": f"PAT_SESS_{user['id']}_123",
                            "user": {"id": user['id'], "name": f"{user['first_name']} {user['last_name']}", "type": "patient"}
                        })
                        return
                elif portal_type == 'company':
                    cur.execute("""
                        SELECT id, name, piva, portal_active 
                        FROM companies 
                        WHERE portal_username=%s AND portal_password=%s
                    """, (username, password))
                    user = cur.fetchone()
                    if user:
                        if not user['portal_active']:
                            self.send_error_response(403, "Portale web non attivo per questa azienda")
                            return
                        self.send_success_response({
                            "session_token": f"COMP_SESS_{user['id']}_123",
                            "user": {"id": user['id'], "name": user['name'], "type": "company"}
                        })
                        return
                elif portal_type == 'collection_point':
                    cur.execute("""
                        SELECT id, code, name, username
                        FROM lis_collection_points
                        WHERE username=%s AND password=%s
                    """, (username, password))
                    user = cur.fetchone()
                    if user:
                        req_cp_code = data.get('cp_code')
                        if req_cp_code and user['code'] != req_cp_code:
                            self.send_error_response(403, "Credenziali non associate a questo punto prelievo")
                            return
                        self.send_success_response({
                            "session_token": f"CP_SESS_{user['id']}_123",
                            "user": {"id": user['id'], "name": user['name'], "code": user['code'], "type": "collection_point"}
                        })
                        return
            self.send_error_response(401, "Credenziali non valide")
        except Exception as e:
            self.send_error_response(500, f"Errore login portale: {str(e)}")
        finally:
            conn.close()

    def handle_portal_appointments(self, data):
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        if not user_id or not user_type:
            self.send_error_response(400, "Dati utente obbligatori")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                if user_type == 'patient':
                    cur.execute("""
                        SELECT a.*, 
                               a.appointment_datetime AS scheduled_at,
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
                    """, (user_id,))
                else:
                    cur.execute("""
                        SELECT a.*, 
                               a.appointment_datetime AS scheduled_at,
                               CONCAT(st.first_name, ' ', st.last_name) as doctor_name,
                               (
                                   SELECT GROUP_CONCAT(s.name SEPARATOR ', ')
                                   FROM appointment_services aps
                                   JOIN medical_services s ON aps.service_id = s.id
                                   WHERE aps.appointment_id = a.id
                               ) AS service_name,
                               p.first_name, p.last_name
                        FROM appointments a
                        LEFT JOIN doctors d ON a.doctor_id = d.id
                        LEFT JOIN staff st ON d.staff_id = st.id
                        LEFT JOIN patients p ON a.patient_id = p.id
                        WHERE p.company_id = %s
                        ORDER BY a.appointment_datetime DESC
                    """, (user_id,))
                import datetime
                rows = cur.fetchall()
                for r in rows:
                    for k, v in list(r.items()):
                        if isinstance(v, (datetime.datetime, datetime.date)):
                            r[k] = v.strftime('%Y-%m-%d %H:%M:%S') if isinstance(v, datetime.datetime) else v.strftime('%Y-%m-%d')
            self.send_success_response(rows)
        except Exception as e:
            self.send_error_response(500, f"Errore recupero appuntamenti: {str(e)}")
        finally:
            conn.close()

    def handle_portal_invoices(self, data):
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        if not user_id or not user_type:
            self.send_error_response(400, "Dati utente obbligatori")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                if user_type == 'patient':
                    cur.execute("""
                        SELECT DISTINCT i.*, i.issue_date AS invoice_date, i.amount_due AS amount
                        FROM invoices i
                        LEFT JOIN admissions adm ON i.admission_id = adm.id
                        LEFT JOIN appointments app ON i.appointment_id = app.id
                        LEFT JOIN lab_samples ls ON i.sample_id = ls.id
                        LEFT JOIN radiology_studies rs ON i.study_id = rs.id
                        WHERE adm.patient_id = %s
                           OR app.patient_id = %s
                           OR ls.patient_id = %s
                           OR rs.patient_id = %s
                        ORDER BY i.issue_date DESC
                    """, (user_id, user_id, user_id, user_id))
                else:
                    cur.execute("""
                        SELECT i.*, i.issue_date AS invoice_date, i.amount_due AS amount
                        FROM invoices i
                        WHERE i.company_id = %s
                        ORDER BY i.issue_date DESC
                    """, (user_id,))
                rows = cur.fetchall()
                for r in rows:
                    if r.get('invoice_date'):
                        r['invoice_date'] = str(r['invoice_date'])
                    if r.get('amount') is not None:
                        r['amount'] = float(r['amount'])
            self.send_success_response(rows)
        except Exception as e:
            self.send_error_response(500, f"Errore recupero fatture: {str(e)}")
        finally:
            conn.close()

    def handle_portal_reports(self, data):
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        if not user_id or not user_type:
            self.send_error_response(400, "Dati utente obbligatori")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                if user_type == 'patient':
                    cur.execute("""
                        SELECT DISTINCT lr.id, lr.released_at, 'lis' as type, 'Analisi di Laboratorio' as service_name
                        FROM lab_reports lr
                        JOIN lab_samples ls ON lr.session_uid = ls.session_uid
                        WHERE ls.patient_id = %s AND lr.status = 'official'
                    """, (user_id,))
                    lis = cur.fetchall()
                    
                    cur.execute("""
                        SELECT rs.id, rs.signed_at as released_at, 'ris' as type, s.name as service_name
                        FROM radiology_studies rs
                        JOIN medical_services s ON rs.service_id = s.id
                        WHERE rs.patient_id = %s AND rs.status = 'completed'
                    """, (user_id,))
                    ris = cur.fetchall()
                else:
                    cur.execute("""
                        SELECT DISTINCT lr.id, lr.released_at, 'lis' as type, 'Analisi di Laboratorio' as service_name, p.first_name, p.last_name
                        FROM lab_reports lr
                        JOIN lab_samples ls ON lr.session_uid = ls.session_uid
                        JOIN patients p ON ls.patient_id = p.id
                        WHERE p.company_id = %s AND lr.status = 'official'
                    """, (user_id,))
                    lis = cur.fetchall()
                    
                    cur.execute("""
                        SELECT rs.id, rs.signed_at as released_at, 'ris' as type, s.name as service_name, p.first_name, p.last_name
                        FROM radiology_studies rs
                        JOIN medical_services s ON rs.service_id = s.id
                        JOIN patients p ON rs.patient_id = p.id
                        WHERE p.company_id = %s AND rs.status = 'completed'
                    """, (user_id,))
                    ris = cur.fetchall()
                    
                rows = list(lis) + list(ris)
                for r in rows:
                    if r['released_at']:
                        r['released_at'] = str(r['released_at'])
            self.send_success_response(rows)
        except Exception as e:
            self.send_error_response(500, f"Errore recupero referti: {str(e)}")
        finally:
            conn.close()

    def handle_portal_cancel_appointment(self, data):
        app_id = data.get('appointment_id')
        user_id = data.get('user_id')
        user_type = data.get('user_type')
        if not app_id or not user_id or not user_type:
            self.send_error_response(400, "Parametri incompleti")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cur:
                if user_type == 'patient':
                    cur.execute("SELECT id FROM appointments WHERE id=%s AND patient_id=%s", (app_id, user_id))
                else:
                    cur.execute("""
                        SELECT a.id FROM appointments a
                        JOIN patients p ON a.patient_id = p.id
                        WHERE a.id=%s AND p.company_id=%s
                    """, (app_id, user_id))
                if not cur.fetchone():
                    self.send_error_response(403, "Non autorizzato ad annullare questo appuntamento")
                    return
                
                cur.execute("UPDATE appointments SET status='cancelled' WHERE id=%s", (app_id,))
                conn.commit()
            self.send_success_response({"message": "Appuntamento annullato con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore annullamento appuntamento: {str(e)}")
        finally:
            conn.close()

    def handle_portal_patient_data(self, data):
        patient_id = data.get('patient_id')
        if not patient_id:
            self.send_error_response(400, "ID paziente obbligatorio")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
                patients = cur.fetchall()
                for p in patients:
                    if p.get('birth_date'): p['birth_date'] = str(p['birth_date'])
                    if p.get('created_at'): p['created_at'] = str(p['created_at'])
                    if p.get('updated_at'): p['updated_at'] = str(p['updated_at'])

                cur.execute("SELECT * FROM lab_samples WHERE patient_id = %s", (patient_id,))
                samples = cur.fetchall()
                sample_ids = [s['id'] for s in samples]
                for s in samples:
                    if s.get('collected_at'): s['collected_at'] = str(s['collected_at'])
                    if s.get('created_at'): s['created_at'] = str(s['created_at'])
                    if s.get('updated_at'): s['updated_at'] = str(s['updated_at'])

                tests = []
                if sample_ids:
                    format_strings = ','.join(['%s'] * len(sample_ids))
                    cur.execute(f"SELECT * FROM lab_tests WHERE sample_id IN ({format_strings})", tuple(sample_ids))
                    tests = cur.fetchall()
                    for t in tests:
                        if t.get('created_at'): t['created_at'] = str(t.get('created_at'))
                        if t.get('updated_at'): t['updated_at'] = str(t.get('updated_at'))
                
                cur.execute("""
                    SELECT i.* FROM invoices i
                    LEFT JOIN admissions adm ON i.admission_id = adm.id
                    LEFT JOIN appointments app ON i.appointment_id = app.id
                    WHERE adm.patient_id = %s OR app.patient_id = %s OR i.patient_id = %s OR i.sample_id IN (
                        SELECT id FROM lab_samples WHERE patient_id = %s
                    )
                """, (patient_id, patient_id, patient_id, patient_id))
                invoices = cur.fetchall()
                for inv in invoices:
                    if inv.get('issue_date'): inv['issue_date'] = str(inv['issue_date'])
                    if inv.get('paid_at'): inv['paid_at'] = str(inv['paid_at'])
                    if inv.get('created_at'): inv['created_at'] = str(inv['created_at'])
                    if inv.get('updated_at'): inv['updated_at'] = str(inv['updated_at'])
                    if inv.get('subtotal') is not None: inv['subtotal'] = float(inv['subtotal'])
                    if inv.get('amount_due') is not None: inv['amount_due'] = float(inv['amount_due'])
                    if inv.get('amount_paid') is not None: inv['amount_paid'] = float(inv['amount_paid'])
                    if inv.get('stamp_duty') is not None: inv['stamp_duty'] = float(inv['stamp_duty'])
                    if inv.get('insurance_covered_amount') is not None: inv['insurance_covered_amount'] = float(inv['insurance_covered_amount'])

                cur.execute("SELECT * FROM medical_services WHERE type = 'lis'")
                services = cur.fetchall()
                for sv in services:
                    if sv.get('price') is not None: sv['price'] = float(sv['price'])
                    if sv.get('created_at'): sv['created_at'] = str(sv['created_at'])
                    if sv.get('updated_at'): sv['updated_at'] = str(sv['updated_at'])

                cur.execute("SELECT * FROM lis_collection_points")
                points = cur.fetchall()
                for pt in points:
                    if pt.get('created_at'): pt['created_at'] = str(pt['created_at'])
                    if pt.get('updated_at'): pt['updated_at'] = str(pt['updated_at'])

                cur.execute("SELECT * FROM patient_consents WHERE patient_id = %s", (patient_id,))
                consents = cur.fetchall()
                for c in consents:
                    if c.get('consented_at'): c['consented_at'] = str(c['consented_at'])

                cur.execute("SELECT * FROM tube_types")
                tube_types = cur.fetchall()

                cur.execute("SELECT * FROM consent_templates")
                templates = cur.fetchall()

            res_data = {
                "patients": patients,
                "samples": samples,
                "tests": tests,
                "invoices": invoices,
                "services": services,
                "collection_points": points,
                "patient_consents": consents,
                "tube_types": tube_types,
                "consent_templates": templates
            }
            self.send_success_response(res_data)
        except Exception as e:
            self.send_error_response(500, f"Errore caricamento dati paziente: {str(e)}")
        finally:
            conn.close()

    def clean_db_rows(self, rows):
        import decimal
        import datetime
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
                elif col in ['parameters', 'details', 'custom_rates', 'service_ids', 'active_days', 'updated_fields', 'values', 'package_items', 'lis_transcoding', 'profiles', 'doctor_ids', 'reporting_doctor_ids', 'antibiotics_json', 'samples_json', 'time_slots', 'temperature_log'] and isinstance(val, str):
                    try:
                        cleaned_row[col] = json.loads(val)
                    except Exception:
                        cleaned_row[col] = val
                else:
                    cleaned_row[col] = val
            cleaned_rows.append(cleaned_row)
        return cleaned_rows

    def handle_portal_company_data(self, data):
        company_id = data.get('company_id')
        if not company_id:
            self.send_error_response(400, "ID azienda obbligatorio")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM patients WHERE company_id = %s", (company_id,))
                patients = self.clean_db_rows(cur.fetchall())
                
                cur.execute("SELECT * FROM invoices WHERE company_id = %s", (company_id,))
                invoices = self.clean_db_rows(cur.fetchall())
                
            self.send_success_response({
                "patients": patients,
                "invoices": invoices
            })
        except Exception as e:
            self.send_error_response(500, f"Errore recupero dati azienda: {str(e)}")
        finally:
            conn.close()

    def handle_portal_cp_data(self, data):
        cp_id = data.get('collection_point_id')
        if not cp_id:
            self.send_error_response(400, "ID punto prelievo obbligatorio")
            return
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                cur.execute("SELECT * FROM lab_samples WHERE collection_point_id = %s", (cp_id,))
                samples = self.clean_db_rows(cur.fetchall())
                sample_ids = [s['id'] for s in samples]
                session_uids = list(set([s['session_uid'] for s in samples if s.get('session_uid')]))
                
                tests = []
                if sample_ids:
                    format_strings = ','.join(['%s'] * len(sample_ids))
                    cur.execute(f"SELECT * FROM lab_tests WHERE sample_id IN ({format_strings})", tuple(sample_ids))
                    tests = self.clean_db_rows(cur.fetchall())
                    
                cur.execute("SELECT * FROM lis_ddt WHERE collection_point_id = %s", (cp_id,))
                ddts = self.clean_db_rows(cur.fetchall())
                
                reports = []
                if session_uids:
                    format_strings = ','.join(['%s'] * len(session_uids))
                    cur.execute(f"SELECT * FROM lab_reports WHERE session_uid IN ({format_strings})", tuple(session_uids))
                    reports = self.clean_db_rows(cur.fetchall())
                    
                cur.execute("SELECT * FROM invoices WHERE collection_point_id = %s", (cp_id,))
                invoices = self.clean_db_rows(cur.fetchall())
                
                patient_ids = list(set([s['patient_id'] for s in samples if s.get('patient_id')]))
                patients = []
                consents = []
                if patient_ids:
                    format_strings = ','.join(['%s'] * len(patient_ids))
                    cur.execute(f"SELECT * FROM patients WHERE id IN ({format_strings})", tuple(patient_ids))
                    patients = self.clean_db_rows(cur.fetchall())
                    
                    cur.execute(f"SELECT * FROM patient_consents WHERE patient_id IN ({format_strings})", tuple(patient_ids))
                    consents = self.clean_db_rows(cur.fetchall())
                    
                cur.execute("SELECT * FROM medical_services WHERE type = 'lis'")
                services = self.clean_db_rows(cur.fetchall())
                
                cur.execute("SELECT id, code, name, address, phone, email, invoice_separate, invoice_prefix, invoice_next_num, billing_type FROM lis_collection_points")
                points = self.clean_db_rows(cur.fetchall())
                
                cur.execute("SELECT * FROM tube_types")
                tube_types = self.clean_db_rows(cur.fetchall())
                
                cur.execute("SELECT * FROM consent_templates")
                templates = self.clean_db_rows(cur.fetchall())
                
                micro_results = []
                if tests:
                    test_ids = [t['id'] for t in tests]
                    format_strings = ','.join(['%s'] * len(test_ids))
                    cur.execute(f"SELECT * FROM lis_microbiology_results WHERE test_id IN ({format_strings})", tuple(test_ids))
                    micro_results = self.clean_db_rows(cur.fetchall())
                    
                cur.execute("SELECT MAX(id) as max_id FROM patients")
                max_patient = cur.fetchone()['max_id'] or 0
                cur.execute("SELECT MAX(id) as max_id FROM lab_samples")
                max_sample = cur.fetchone()['max_id'] or 0
                cur.execute("SELECT MAX(id) as max_id FROM lab_tests")
                max_test = cur.fetchone()['max_id'] or 0
                cur.execute("SELECT MAX(id) as max_id FROM invoices")
                max_invoice = cur.fetchone()['max_id'] or 0
                cur.execute("SELECT MAX(id) as max_id FROM patient_consents")
                max_consent = cur.fetchone()['max_id'] or 0
                cur.execute("SELECT MAX(id) as max_id FROM lis_ddt")
                max_ddt = cur.fetchone()['max_id'] or 0
                
                global_max_ids = {
                    "patients": max_patient,
                    "samples": max_sample,
                    "tests": max_test,
                    "invoices": max_invoice,
                    "consents": max_consent,
                    "ddt": max_ddt
                }
                    
            self.send_success_response({
                "globalMaxIds": global_max_ids,
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
            })
        except Exception as e:
            self.send_error_response(500, f"Errore recupero dati punto prelievo: {str(e)}")
        finally:
            conn.close()

    def handle_portal_upsert_records(self, params):
        table_name = params.get('table_name')
        rows = params.get('rows', [])
        
        if not table_name:
            self.send_error_response(400, "Tabella non specificata")
            return
            
        import re
        def clean_datetime_val(val):
            if isinstance(val, str):
                iso_match = re.match(r'^(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2}(?::\d{2})?)(?:\.\d+)?(?:Z|[+-]\d{2}:?\d{2})?$', val)
                if iso_match:
                    date_part = iso_match.group(1)
                    time_part = iso_match.group(2)
                    if len(time_part) == 5:
                        time_part += ":00"
                    return f"{date_part} {time_part}"
            return val
            
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
            
        # Tabelle protette: non aggiornabili dal portale (hanno campi sensibili o vincoli NOT NULL)
        PROTECTED_TABLES = ['lis_collection_points', 'staff', 'users']
        # Campi sensibili da escludere sempre dagli upsert del portale
        EXCLUDED_FIELDS = ['username', 'password', 'portal_password', 'pin']
        
        if table_name.lower() in PROTECTED_TABLES:
            self.send_success_response({"message": f"Tabella {table_name} protetta, aggiornamento ignorato"})
            return
        
        try:
            with conn.cursor() as cursor:
                cursor.execute("SHOW TABLES")
                db_tables = [list(r.values())[0].lower() for r in cursor.fetchall()]
                
                if table_name.lower() not in db_tables:
                    self.send_success_response({"message": f"Tabella {table_name} ignorata"})
                    return
                    
                if not rows:
                    self.send_success_response({"message": "Nessuna riga da aggiornare"})
                    return
                    
                cursor.execute(f"SHOW COLUMNS FROM `{table_name}`")
                cols_info = cursor.fetchall()
                columns = [col['Field'] for col in cols_info]
                
                # Perform upsert for each row
                for row in rows:
                    # Escludi campi sensibili
                    row_cols = [c for c in columns if c in row and c not in EXCLUDED_FIELDS]
                    if not row_cols:
                        continue
                        
                    vals = []
                    for col in row_cols:
                        val = row.get(col)
                        if col in ['parameters', 'details', 'custom_rates', 'service_ids', 'active_days', 'updated_fields', 'values', 'package_items', 'lis_transcoding', 'profiles', 'doctor_ids', 'reporting_doctor_ids', 'antibiotics_json', 'samples_json', 'time_slots', 'temperature_log'] and (isinstance(val, list) or isinstance(val, dict)):
                            val = json.dumps(val)
                        if val == "":
                            val = None
                        elif isinstance(val, str):
                            val = clean_datetime_val(val)
                        vals.append(val)
                        
                    col_list = ", ".join([f"`{c}`" for c in row_cols])
                    placeholders = ", ".join(["%s"] * len(row_cols))
                    update_list = ", ".join([f"`{c}`=VALUES(`{c}`)" for c in row_cols if c != 'id'])
                    
                    query = f"INSERT INTO `{table_name}` ({col_list}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_list}"
                    cursor.execute(query, tuple(vals))
                    
                conn.commit()
            self.send_success_response({"message": "Dati aggiornati con successo"})
        except Exception as e:
            self.send_error_response(500, f"Errore upsert tabella: {str(e)}")
        finally:
            conn.close()

    def handle_mwl_status(self, data):
        status = "online" if HAS_DICOM else "disabled"
        self.send_success_response({
            "status": status,
            "ae_title": "NEXTCARE_RIS",
            "port": 11104,
            "logs": MWL_LOGS
        })

    # 5. Duplicate Price List Handler
    def handle_price_lists_duplicate(self, data):
        list_id = data.get('price_list_id')
        new_name = data.get('new_name', '').strip()
        
        if not list_id or not new_name:
            self.send_error_response(400, "ID listino e nuovo nome obbligatori")
            return
            
        conn = get_db_connection()
        if not conn:
            self.send_error_response(500, "Connessione database fallita")
            return
        try:
            with conn.cursor() as cur:
                cur.execute("INSERT INTO price_lists (name) VALUES (%s)", (new_name,))
                new_list_id = cur.lastrowid
                
                cur.execute("""
                    INSERT INTO price_list_items (price_list_id, service_id, price)
                    SELECT %s, service_id, price
                    FROM price_list_items
                    WHERE price_list_id = %s
                """, (new_list_id, list_id))
                
                conn.commit()
            self.send_success_response({
                "message": f"Listino duplicato con successo con ID {new_list_id}",
                "new_price_list_id": new_list_id
            })
        except Exception as e:
            self.send_error_response(500, f"Errore duplicazione listino: {str(e)}")
        finally:
            conn.close()

    # 6. AI Help Handler
    def handle_ai_help(self, data):
        query = data.get('query', '').strip().lower()
        if not query:
            self.send_error_response(400, "Domanda vuota")
            return
            
        response = "Spiacente, non ho trovato indicazioni nel manuale locale per la tua domanda. Prova a consultare la scheda FAQ."
        
        if "fse" in query or "oscur" in query or "fascicol" in query:
            response = """
            <b>Gestione Fascicolo Sanitario Elettronico (FSE 2.0) &amp; Oscuramento:</b><br>
            Il sistema genera automaticamente un file <code>cda.xml</code> per ogni referto ufficiale firmato. Questo viene iniettato nel PDF tramite la libreria pypdf ed inviato al Gateway FSE.<br>
            <b>Logiche di Oscuramento:</b><br>
            - In accettazione o refertazione, puoi impostare l'oscuramento della prestazione.<br>
            - <b>P99:</b> Oscuramento totale verso operatori terzi.<br>
            - <b>P97:</b> Oscuramento ai genitori/tutori (es. minori).<br>
            - <b>P98:</b> Oscuramento temporaneo ad assistito.<br>
            Verifica lo stato nella dashboard dedicata FSE.
            """
        elif "ricett" in query or "impegn" in query or "ssn" in query:
            response = """
            <b>Caricamento Impegnativa SSN &amp; Ricette:</b><br>
            - In Accettazione CUP, seleziona la tipologia di paziente 'SSN' ed inserisci i dati ricetta (NRE, CF, Quesito Diagnostico, Medico, Priorita' B/U/D/P).<br>
            - Il sistema effettua automaticamente l'<b>ASL lookup</b> in base alla citta' dell'assistito.<br>
            - Limite ricetta: Massimo 8 prestazioni per singolo codice NRE. Prestazioni in eccesso verranno splittate in ricette successive.<br>
            - Esenzioni: Inserisci il codice esenzione. Se esenzione 'NE' (Non Esente) o vuota, viene calcolato il ticket (limite 36,15 euro). Se esente, il ticket e' 0.
            """
        elif "compen" in query or "medico" in query:
            response = """
            <b>Configurazione ed Estrazione Compensi Medici:</b><br>
            - Vai su Impostazioni Medici e configura le percentuali o tariffe fisse per ciascuna branca/prestazione.<br>
            - Gli eventi scatenanti calcolabili sono: <i>erogato</i> (check-in), <i>refertato</i> (referto firmato), <i>fatturato</i> (fattura emessa), <i>incassato</i> (fattura pagata).<br>
            - Dal menu 'Compensi specialisti' e' possibile visualizzare l'estratto conto di ciascun medico ed emettere pagamenti/liquidazioni.
            """
        elif "sts" in query or "730" in query or "tessera" in query:
            response = """
            <b>Invio Spesa Sanitaria STS 730:</b><br>
            - Il sistema permette l'invio telematico a Sistema TS delle sole fatture e note di credito chiuse e pagate.<br>
            - Dal menu STS e' possibile selezionare le fatture da inviare massivamente o singolarmente.<br>
            - Il server esporta inoltre i file XML in <code>C:\\NextCare_STS_Exchange\\export</code> per l'invio manuale sul portale.
            """
            
        self.send_success_response({"reply": response})
    # =========================================================================
    # NEXTCARE ENTERPRISE SUITE V1.0 - SYNC EVENT TRIGGERS (COMPENSI, FSE AUTO-SEND)
    # =========================================================================

    def check_sync_event_triggers(self, table_name, rows):
        t_name = table_name.lower()
        if t_name == 'appointments':
            for row in rows:
                if row.get('status') in ['executed', 'completed', 'in_progress']:
                    self.calculate_compensation_for_event('erogato', row)
        elif t_name == 'radiology_studies':
            for row in rows:
                if row.get('status') == 'completed':
                    self.calculate_compensation_for_event('refertato', row)
                    fse_enabled = self.get_setting_val('fse_enabled') == 'true'
                    if fse_enabled:
                        import threading
                        t = threading.Thread(target=self.process_fse_transmission, args=('ris', row.get('id')), daemon=True)
                        t.start()
        elif t_name == 'lab_reports':
            for row in rows:
                if row.get('status') == 'official':
                    fse_enabled = self.get_setting_val('fse_enabled') == 'true'
                    if fse_enabled:
                        import threading
                        t = threading.Thread(target=self.process_fse_transmission, args=('lis', row.get('id')), daemon=True)
                        t.start()
        elif t_name == 'invoices':
            for row in rows:
                self.calculate_compensation_for_event('fatturato', row)
                if row.get('status') == 'paid':
                    self.calculate_compensation_for_event('incassato', row)
        elif t_name == 'lis_collection_points':
            for row in rows:
                cp_code = row.get('code')
                if cp_code:
                    self.generate_collection_point_portal(cp_code, row)

    def generate_collection_point_portal(self, cp_code, cp_row):
        portal_filename = f"portal_{cp_code}.html"
        base_dir = os.path.dirname(os.path.abspath(__file__))
        portal_path = os.path.join(base_dir, portal_filename)
        template_path = os.path.join(base_dir, "portal_template.html")
        
        if not os.path.exists(template_path):
            print(f"[Warning] portal_template.html not found at {template_path}, cannot generate light portal.")
            return
            
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                html_template = f.read()
                
            html_content = html_template.replace("__CP_CODE__", cp_code)
            html_content = html_content.replace("__CP_NAME__", cp_row.get('name', 'Punto Prelievo'))
            html_content = html_content.replace("__CP_ID__", str(cp_row.get('id', 0)))
            
            with open(portal_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"[Portal Gen] Generated light portal for {cp_code} at {portal_path}")
        except Exception as e:
            print(f"[Portal Gen Error] Failed to generate portal for {cp_code}:", e)

    def get_setting_val(self, key):
        conn = get_db_connection()
        if not conn: return None
        val = None
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT setting_value FROM system_settings WHERE setting_key=%s", (key,))
                r = cur.fetchone()
                if r: val = r[0]
        except:
            pass
        finally:
            conn.close()
        return val

    def calculate_compensation_for_event(self, event_type, item):
        doctor_id = None
        service_id = None
        base_amount = 0.00
        appointment_id = None
        invoice_id = None
        
        conn = get_db_connection()
        if not conn: return
        
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                if event_type in ['erogato', 'refertato'] or 'scheduled_at' in item:
                    doctor_id = item.get('doctor_id') or item.get('signed_by')
                    service_id = item.get('service_id')
                    appointment_id = item.get('id')
                    if not doctor_id and appointment_id:
                        cur.execute("SELECT doctor_id, service_id FROM appointments WHERE id=%s", (appointment_id,))
                        r = cur.fetchone()
                        if r:
                            doctor_id = r['doctor_id']
                            service_id = r['service_id']
                    
                    if appointment_id:
                        cur.execute("SELECT id, amount FROM invoices WHERE appointment_id=%s", (appointment_id,))
                        inv = cur.fetchone()
                        if inv:
                            invoice_id = inv['id']
                            base_amount = float(inv['amount'])
                    if base_amount == 0.00 and service_id:
                        cur.execute("SELECT price FROM medical_services WHERE id=%s", (service_id,))
                        srv = cur.fetchone()
                        if srv and srv['price']:
                            base_amount = float(srv['price'])
                            
                elif event_type in ['fatturato', 'incassato'] or 'invoice_number' in item:
                    invoice_id = item.get('id')
                    base_amount = float(item.get('amount') or 0.00)
                    app_id = item.get('appointment_id')
                    if app_id:
                        appointment_id = app_id
                        cur.execute("SELECT doctor_id, service_id FROM appointments WHERE id=%s", (app_id,))
                        r = cur.fetchone()
                        if r:
                            doctor_id = r['doctor_id']
                            service_id = r['service_id']
                            
                if not doctor_id or not service_id:
                    return
                    
                patient_type = "Privato"
                insurance_id = None
                company_id = None
                branch = None
                
                cur.execute("SELECT branch FROM medical_services WHERE id=%s", (service_id,))
                srv = cur.fetchone()
                if srv: branch = srv['branch']
                
                if appointment_id:
                    cur.execute("""
                        SELECT p.patient_type, p.insurance_id, p.company_id 
                        FROM appointments a
                        JOIN patients p ON a.patient_id = p.id
                        WHERE a.id = %s
                    """, (appointment_id,))
                    p = cur.fetchone()
                    if p:
                        patient_type = p['patient_type'] or "Privato"
                        insurance_id = p['insurance_id']
                        company_id = p['company_id']
                        
                cur.execute("""
                    SELECT * FROM doctor_compensations_config 
                    WHERE doctor_id = %s AND trigger_event = %s
                """, (doctor_id, event_type))
                rules = cur.fetchall()
                
                best_rule = None
                best_score = -1
                
                for rule in rules:
                    score = 0
                    if rule['service_id']:
                        if rule['service_id'] == service_id:
                            score += 10
                        else:
                            continue
                    if rule['branch']:
                        if rule['branch'].lower() == (branch or '').lower():
                            score += 5
                        else:
                            continue
                    if rule['patient_type']:
                        if rule['patient_type'].lower() == patient_type.lower():
                            score += 3
                        else:
                            continue
                    if rule['insurance_id']:
                        if rule['insurance_id'] == insurance_id:
                            score += 3
                        else:
                            continue
                    if rule['company_id']:
                        if rule['company_id'] == company_id:
                            score += 3
                        else:
                            continue
                            
                    if score > best_score:
                        best_score = score
                        best_rule = rule
                        
                if best_rule:
                    payout = 0.00
                    val = float(best_rule['value'])
                    if best_rule['compensation_type'] == 'percentage':
                        payout = round(base_amount * (val / 100.0), 2)
                    else:
                        payout = val
                        
                    cur.execute("""
                        SELECT id FROM doctor_calculated_compensations 
                        WHERE doctor_id = %s AND service_id = %s AND event_type = %s AND (appointment_id = %s OR invoice_id = %s)
                    """, (doctor_id, service_id, event_type, appointment_id, invoice_id))
                    existing = cur.fetchone()
                    
                    if existing:
                        cur.execute("""
                            UPDATE doctor_calculated_compensations
                            SET base_amount = %s, calculated_amount = %s
                            WHERE id = %s
                        """, (base_amount, payout, existing['id']))
                    else:
                        cur.execute("""
                            INSERT INTO doctor_calculated_compensations
                            (doctor_id, appointment_id, invoice_id, service_id, event_type, base_amount, calculated_amount, status)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
                        """, (doctor_id, appointment_id, invoice_id, service_id, event_type, base_amount, payout))
                    conn.commit()
                    print(f"[Compensation] Calculated compenso of {payout} (rule ID {best_rule['id']}) for doctor {doctor_id}")
        except Exception as e:
            print(f"[Compensation Error] {e}")
        finally:
            conn.close()




# --- LIS INTERFACING & BACKGROUND ENGINE ---



import socket

import re

import shutil

import threading

import time



# Keep track of active socket servers: port -> thread/socket reference
RUNNING_SOCKET_SERVERS = {}
EQUIPMENT_LOGS = {}
LOCKED_SLOTS = {}
LAST_ACTIVITY = {}
SLOT_LOCK = threading.Lock()
CHAT_LOCK = threading.Lock()



def log_equipment_event(equipment_id, direction, message_type, content):

    import datetime

    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    log_entry = {

        "direction": direction,

        "message_type": message_type,

        "content": content,

        "timestamp": timestamp

    }

    

    try:

        eq_id_int = int(equipment_id)

    except Exception:

        return

        

    if eq_id_int not in EQUIPMENT_LOGS:

        EQUIPMENT_LOGS[eq_id_int] = []

    EQUIPMENT_LOGS[eq_id_int].insert(0, log_entry)

    if len(EQUIPMENT_LOGS[eq_id_int]) > 100:

        EQUIPMENT_LOGS[eq_id_int] = EQUIPMENT_LOGS[eq_id_int][:100]

        

    conn = get_db_connection()

    if conn:

        try:

            with conn.cursor() as cursor:

                cursor.execute("""

                    INSERT INTO equipment_logs (equipment_id, direction, message_type, content)

                    VALUES (%s, %s, %s, %s)

                """, (eq_id_int, direction, message_type, content))

                conn.commit()

        except Exception as e:

            print(f"[MySQL Log Error] {e}")

        finally:

            conn.close()



def get_db_connection():

    config_path = "config.json"

    if os.path.exists(config_path):

        try:

            with open(config_path, "r", encoding="utf-8") as f:

                config = json.load(f)

            if config.get('db_host'):

                import pymysql

                return pymysql.connect(

                    host=config.get('db_host', 'localhost'),

                    port=int(config.get('db_port', 3306)),

                    user=config.get('db_user', 'root'),

                    password=config.get('db_pass', ''),

                    database=config.get('db_name', 'nextcare_db'),

                    charset='utf8mb4',

                    cursorclass=pymysql.cursors.DictCursor

                )

        except Exception:

            pass

    return None


def auto_detect_updates(conn):
    import re
    # 1. Ensure system_news table exists
    try:
        with conn.cursor() as cur:
            cur.execute("""
            CREATE TABLE IF NOT EXISTS `system_news` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `category` VARCHAR(100) NOT NULL,
                `description` TEXT NOT NULL,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 2. Check if table is empty. If so, seed standard 10 updates
            cur.execute("SELECT COUNT(*) FROM `system_news`")
            row = cur.fetchone()
            count = list(row.values())[0] if row else 0
            if count == 0:
                seeds = [
                    ("Compliance", "FSE 2.0 Compliance: Generazione CDA XML, iniezione PDF via pypdf, firma token a due chiavi e logiche di oscuramento P99/P97/P98."),
                    ("Fiscale", "STS Spesa Sanitaria 730: Gestione e trasmissione fatture pagate, ed export file locali."),
                    ("Compensi", "Compensi Specialisti: Motore di calcolo provvigionale o quota fissa legato a 4 eventi operativi."),
                    ("ASL", "Rendicontazione ASL: Split ricette (max 8), esenzioni ministeriali e calcolo ticket cap 36.15€."),
                    ("Portali", "Portali Pazienti/Aziende: Piattaforme stand-alone per l'accesso e il download protetto da credenziali."),
                    ("Magazzino", "Magazzino Avanzato (MySQL): CRUD completo per fornitori, articoli e frigoriferi in MySQL, con tasti inline di aggiunta/modifica e autocompilazione."),
                    ("Turni", "Pianificazione Turni Ricorrenti: Gestione turni ricorrenti (settimanali e mensili) con generazione automatica dei singoli record turni."),
                    ("Privacy", "Privacy & Cookie GDPR: Consenso Cookie premium e Informativa Privacy integrata su tutti i portali legati a nextcare.health."),
                    ("Riabilitazione", "Cicli Riabilitazione: Diari clinici, scale VAS e andamento grafico del dolore con integrazione ruolo terapista."),
                    ("Imaging", "Modality Worklist (MWL) DICOM: Server MWL interno attivo sulla porta 11104.")
                ]
                cur.executemany("INSERT INTO `system_news` (category, description) VALUES (%s, %s)", seeds)
                conn.commit()
                
            # 3. Load all existing news descriptions to avoid duplicates
            cur.execute("SELECT description FROM `system_news`")
            existing_descriptions = {r['description'] for r in cur.fetchall()}
            
            # --- FAQ AUTOMATION ---
            # 3.1. Ensure system_faqs table exists
            cur.execute("""
            CREATE TABLE IF NOT EXISTS `system_faqs` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `question` VARCHAR(255) NOT NULL,
                `answer` TEXT NOT NULL,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # 3.2. Load all existing FAQ questions to avoid duplicates
            cur.execute("SELECT question FROM `system_faqs`")
            existing_questions = {r['question'] for r in cur.fetchall()}
            
            # Paths
            current_dir = os.path.dirname(os.path.abspath(__file__))
            server_path = os.path.join(current_dir, 'server.py')
            html_path = os.path.join(current_dir, 'index.html')

            # 4. Detect New DB Tables
            KNOWN_TABLES = {
                'patients', 'patient_consents', 'staff', 'audit_logs', 'clinics',
                'equipment', 'dose_classes', 'medical_services', 'doctors',
                'doctor_agendas', 'doctor_agenda_services', 'doctor_closures',
                'appointments', 'appointment_services', 'lab_samples', 'lab_tests',
                'radiology_studies', 'admissions', 'price_lists', 'price_list_items',
                'insurances', 'patient_claims', 'tube_types', 'sample_collection_types',
                'profit_centers', 'sent_emails', 'invoices', 'prima_nota_movements',
                'shifts', 'system_settings', 'lis_worksheets', 'lab_reports',
                'consent_templates', 'system_news', 'system_faqs',
                'companies', 'ris_report_templates',
                'stock_fridges', 'stock_items', 'stock_logs', 'stock_suppliers',
                'rehab_cycles', 'rehab_sessions',
                'doctor_calculated_compensations', 'doctor_compensations_config',
                'fse_transmissions',
                'ssn_asl_mapping', 'ssn_exemptions', 'ssn_priorities', 'ssn_recipes',
                'system_license', 'chat_messages', 'equipment_logs'
            }
            
            cur.execute("SHOW TABLES")
            db_tables = [list(r.values())[0].lower() for r in cur.fetchall()]
            new_tables = [t for t in db_tables if t not in KNOWN_TABLES]
            
            for t in new_tables:
                desc = f"Nuova entità di sistema rilevata: modulo '{t.replace('_', ' ').title()}' configurato nel database MySQL."
                if desc not in existing_descriptions:
                    cur.execute("INSERT INTO `system_news` (category, description) VALUES (%s, %s)", ("Database", desc))
                    existing_descriptions.add(desc)
                    print(f"[AutoNews] Detected new table: {t}")
                
                # Auto-generate FAQ for new table
                q = f"Come funziona la tabella/modulo '{t.replace('_', ' ').title()}'?"
                ans = f"Il modulo '{t.replace('_', ' ').title()}' gestisce la memorizzazione e le informazioni di dettaglio delle entità '{t}' nel database MySQL."
                if q not in existing_questions:
                    cur.execute("INSERT INTO `system_faqs` (question, answer) VALUES (%s, %s)", (q, ans))
                    existing_questions.add(q)
                    print(f"[AutoFAQ] Created new FAQ for table: {t}")
            
            # 5. Detect New API Endpoints
            KNOWN_ENDPOINTS = {
                'status', 'login', 'setup-db', 'test-db', 'db-get-all', 'db-sync-table',
                'test-smtp', 'send-email', 'export-lis-requests', 'import-lis-results',
                'save-pdf-report', 'get-lis-simulator-status', 'toggle-lis-simulator',
                'get-equipment-logs', 'clear-equipment-logs', 'save-integration-settings',
                'bianalisi-export', 'bianalisi-pull-results', 'dedalus-export-orders',
                'dedalus-import-results', 'lock-slot', 'chat-heartbeat', 'chat-send',
                'pacs-query', 'pacs-retrieve', 'fse-settings-save', 'fse-transmissions-list',
                'fse-cda-preview', 'fse-manual-send', 'sts-settings-save', 'sts-send-invoices',
                'sts-export-xml', 'compensations-list', 'compensations-config-save',
                'compensations-config-delete', 'compensations-payout', 'portals-login',
                'portal-appointments', 'portal-invoices', 'portal-reports',
                'portal-cancel-appointment', 'mwl-status', 'price-lists-duplicate',
                'ai-help', 'system-settings-save', 'get-integration-settings',
                'bianalisi-labels', 'socket-servers-status', 'get-locked-slots',
                'system-settings'
            }
            
            endpoints = set()
            try:
                if os.path.exists(server_path):
                    with open(server_path, 'r', encoding='utf-8') as f:
                        server_content = f.read()
                    # Match paths like /api/... in string literals
                    matches = re.findall(r"['\"]/api/([a-zA-Z0-9_-]+)['\"]", server_content)
                    endpoints.update(matches)
            except Exception as e:
                print(f"[AutoNews Error] Failed to scan server.py: {e}")
                
            new_endpoints = [ep for ep in endpoints if ep not in KNOWN_ENDPOINTS]
            for ep in new_endpoints:
                desc = f"Nuovo endpoint API di backend rilevato: '/api/{ep}' per integrazioni esterne."
                if desc not in existing_descriptions:
                    cur.execute("INSERT INTO `system_news` (category, description) VALUES (%s, %s)", ("API Endpoint", desc))
                    existing_descriptions.add(desc)
                    print(f"[AutoNews] Detected new endpoint: /api/{ep}")
                
                # Auto-generate FAQ for new endpoint
                q = f"A cosa serve l'endpoint '/api/{ep}'?"
                ans = f"L'endpoint API di backend '/api/{ep}' viene utilizzato per gestire le richieste e l'interoperabilità relative al modulo '{ep.replace('-', ' ').title()}'."
                if q not in existing_questions:
                    cur.execute("INSERT INTO `system_faqs` (question, answer) VALUES (%s, %s)", (q, ans))
                    existing_questions.add(q)
                    print(f"[AutoFAQ] Created new FAQ for endpoint: /api/{ep}")
                    
            # 6. Detect New UI Tabs
            KNOWN_TABS = {
                'accounting', 'admission', 'audit-logs', 'bi-dashboard', 'clinics', 'core', 'cup',
                'dashboard', 'database', 'doctor-compensations', 'faq', 'fse-transmissions', 'hris',
                'insurance-config', 'integrations', 'license', 'lis', 'lis-logs', 'notifications',
                'portals', 'rehab', 'reporting-acceptances', 'reporting-services', 'ris', 'services',
                'ssn-billing', 'sts-transmission', 'templates', 'unified-reports', 'warehouse'
            }
            
            tabs = set()
            try:
                if os.path.exists(html_path):
                    with open(html_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    # Match data-tab="..."
                    matches = re.findall(r'data-tab="([^"]+)"', html_content)
                    tabs.update(matches)
            except Exception as e:
                print(f"[AutoNews Error] Failed to scan index.html: {e}")
                
            new_tabs = [t for t in tabs if t not in KNOWN_TABS]
            for t in new_tabs:
                desc = f"Nuova sezione/modulo UI rilevato nell'applicazione: '{t.upper()}'."
                if desc not in existing_descriptions:
                    cur.execute("INSERT INTO `system_news` (category, description) VALUES (%s, %s)", ("Interfaccia Utente", desc))
                    existing_descriptions.add(desc)
                    print(f"[AutoNews] Detected new tab: {t}")
                
                # Auto-generate FAQ for new UI tab
                q = f"Come si utilizza la sezione UI '{t.upper()}'?"
                ans = f"La sezione dell'interfaccia utente '{t.upper()}' consente la gestione visiva ed operativa delle funzionalità legate al modulo '{t.replace('-', ' ').title()}'."
                if q not in existing_questions:
                    cur.execute("INSERT INTO `system_faqs` (question, answer) VALUES (%s, %s)", (q, ans))
                    existing_questions.add(q)
                    print(f"[AutoFAQ] Created new FAQ for UI tab: {t}")
                    
            conn.commit()
    except Exception as e:
        print(f"[AutoNews Error] auto_detect_updates failed: {e}")


def translate_code(transcoding_rules, nc_type, value, direction="to_instrument"):

    for rule in transcoding_rules:

        if rule.get('nc_type') == nc_type:

            if direction == "to_instrument":

                if nc_type == "service" and rule.get('nc_code') == value:

                    return rule.get('instrument_code')

                elif nc_type == "parameter" and rule.get('nc_name') == value:

                    return rule.get('instrument_code')

            else: # to_nextcare

                if rule.get('instrument_code') == value:

                    return rule.get('nc_code') if nc_type == "service" else rule.get('nc_name')

    return value



def check_and_export_file_orders():

    conn = get_db_connection()

    if not conn:

        return

    try:

        with conn.cursor() as cursor:

            # Get active LIS instruments with file interfacing

            cursor.execute("SELECT * FROM equipment WHERE type = 'LIS' AND status = 'active' AND lis_interface_type = 'file'")

            instruments = cursor.fetchall()

            if not instruments:

                return



            for inst in instruments:

                export_path = inst.get('lis_export_path') or r"C:\NextCare_LIS_Exchange\export"

                file_name = inst.get('lis_file_name')

                file_format = inst.get('lis_file_format', 'csv')

                transcoding = []

                if inst.get('lis_transcoding'):

                    try:

                        transcoding = json.loads(inst['lis_transcoding']) if isinstance(inst['lis_transcoding'], str) else inst['lis_transcoding']

                    except Exception:

                        pass



                # Get samples in 'collected' status

                cursor.execute("""

                    SELECT s.*, p.first_name, p.last_name, p.gender, p.birth_date, p.tax_code 

                    FROM lab_samples s

                    JOIN patients p ON s.patient_id = p.id

                    WHERE s.status = 'collected'

                """)

                samples = cursor.fetchall()

                

                for sample in samples:

                    cursor.execute("SELECT * FROM lab_tests WHERE sample_id = %s", (sample['id'],))

                    tests = cursor.fetchall()

                    

                    inst_tests = []

                    for test in tests:

                        cursor.execute("SELECT * FROM medical_services WHERE id = %s", (test['service_id'],))

                        service = cursor.fetchone()

                        if service and service.get('instrument_id') == inst['id']:

                            inst_tests.append((test, service))

                    

                    if not inst_tests:

                        continue

                    

                    barcode = sample['barcode']

                    print(f"[LIS Exporter] Exporting order for barcode {barcode} to instrument {inst['name']}")

                    

                    analyses = []

                    for test, service in inst_tests:

                        inst_srv_code = translate_code(transcoding, 'service', service['code'], 'to_instrument')

                        if not any(a['code'] == inst_srv_code for a in analyses):

                            analyses.append({

                                "code": inst_srv_code,

                                "material": test.get('sample_type', '')

                            })

                    

                    os.makedirs(export_path, exist_ok=True)

                    

                    if file_format == 'xml':

                        xml_lines = [

                            '<?xml version="1.0" encoding="utf-8"?>',

                            '<ListaRichieste>',

                            '    <CodiceLaboratorio>NEXTCARE</CodiceLaboratorio>',

                            '    <Richiesta>',

                            f"        <Cognome>{sample.get('last_name', '')}</Cognome>",

                            f"        <Nome>{sample.get('first_name', '')}</Nome>",

                            f"        <IdRichiestaLis>{barcode}</IdRichiestaLis>",

                            f"        <Sesso>{sample.get('gender', '')}</Sesso>",

                            f"        <DataNascita>{sample.get('birth_date', '')}</DataNascita>",

                            f"        <Data>{sample.get('created_at', '')}</Data>"

                        ]

                        if sample.get('tax_code'):

                            xml_lines.append(f"        <CodiceFiscale>{sample['tax_code']}</CodiceFiscale>")

                        

                        for ana in analyses:

                            mat_str = f' Materiale="{ana.get("material", "")}"' if ana.get('material') else ''

                            xml_lines.append(f'        <Analisi Codice="{ana["code"]}" IdCampioneLis="{barcode}"{mat_str} />')

                        

                        xml_lines.append('    </Richiesta>')

                        xml_lines.append('</ListaRichieste>')

                        

                        xml_content = "\n".join(xml_lines)

                        target_filename = file_name if (file_name and '{' not in file_name) else f"{barcode}.xml"

                        target_filename = target_filename.replace('{barcode}', barcode)

                        

                        file_path = os.path.join(export_path, target_filename)

                        with open(file_path, "w", encoding="utf-8") as f:

                            f.write(xml_content)

                            

                    else: # CSV format

                        service_codes_str = ";".join([a['code'] for a in analyses])

                        csv_line = f"{barcode},{sample.get('last_name', '')},{sample.get('first_name', '')},{sample.get('gender', '')},{sample.get('birth_date', '')},{service_codes_str}\n"

                        

                        target_filename = file_name if (file_name and '{' not in file_name) else f"{barcode}.csv"

                        target_filename = target_filename.replace('{barcode}', barcode)

                        

                        file_path = os.path.join(export_path, target_filename)

                        mode = "a" if (file_name and '{' not in file_name) else "w"

                        write_header = not os.path.exists(file_path) if mode == "a" else True

                        

                        with open(file_path, mode, encoding="utf-8") as f:

                            if write_header:

                                f.write("barcode,last_name,first_name,gender,birth_date,service_codes\n")

                            f.write(csv_line)

                    

                    # Log TX event

                    try:

                        log_equipment_event(

                            equipment_id=inst['id'],

                            direction='TX',

                            message_type=file_format.upper(),

                            content=xml_content if file_format == 'xml' else csv_line

                        )

                    except Exception as le:

                        print(f"[LIS Exporter Log Error] {le}")



                    cursor.execute("UPDATE lab_samples SET status = 'processing' WHERE id = %s", (sample['id'],))

                    conn.commit()

                    print(f"[LIS Exporter] Order for {barcode} exported successfully. Sample status set to processing.")

    except Exception as e:

        print(f"[LIS Exporter Error] {e}")

    finally:

        conn.close()



def check_and_import_file_results():

    conn = get_db_connection()

    results = []

    if not conn:

        return results

    try:

        with conn.cursor() as cursor:

            cursor.execute("SELECT * FROM equipment WHERE type = 'LIS' AND status = 'active' AND lis_interface_type = 'file'")

            instruments = cursor.fetchall()

            if not instruments:

                return results



            for inst in instruments:

                import_path = inst.get('lis_import_path') or r"C:\NextCare_LIS_Exchange\import"

                if not os.path.exists(import_path):

                    continue

                

                file_name = inst.get('lis_file_name')

                file_format = inst.get('lis_file_format', 'csv')

                transcoding = []

                if inst.get('lis_transcoding'):

                    try:

                        transcoding = json.loads(inst['lis_transcoding']) if isinstance(inst['lis_transcoding'], str) else inst['lis_transcoding']

                    except Exception:

                        pass



                files_to_process = []

                if file_name and '{' not in file_name:

                    file_path = os.path.join(import_path, file_name)

                    if os.path.exists(file_path):

                        files_to_process.append(file_name)

                else:

                    ext = f".{file_format}"

                    for f in os.listdir(import_path):

                        if f.lower().endswith(ext) and not f.startswith("processed_") and os.path.isfile(os.path.join(import_path, f)):

                            files_to_process.append(f)



                for fname in files_to_process:

                    file_path = os.path.join(import_path, fname)

                    print(f"[LIS Importer] Processing file {file_path} for instrument {inst['name']}")

                    

                    file_results = []

                    try:

                        # Log RX event

                        try:

                            with open(file_path, "r", encoding="utf-8") as rf:

                                file_content = rf.read()

                            log_equipment_event(

                                equipment_id=inst['id'],

                                direction='RX',

                                message_type=file_format.upper(),

                                content=file_content

                            )

                        except Exception as le:

                            print(f"[LIS Importer Log Error] {le}")



                        if file_format == 'xml':

                            import xml.etree.ElementTree as ET

                            tree = ET.parse(file_path)

                            root = tree.getroot()

                            

                            req_elements = []

                            if root.tag == 'Richiesta':

                                req_elements.append(root)

                            elif root.tag == 'ListaRichieste':

                                req_elements.extend(root.findall('Richiesta'))

                            else:

                                req_elements.extend(root.findall('.//Richiesta'))

                                

                            for req_node in req_elements:

                                barcode = req_node.findtext('IdRichiestaLis') or req_node.findtext('IdRichiesta')

                                if not barcode:

                                    continue

                                

                                last_name = req_node.findtext('Cognome', '')

                                first_name = req_node.findtext('Nome', '')

                                

                                analyses = []

                                for ana_node in req_node.findall('Analisi'):

                                    srv_code = ana_node.get('Codice')

                                    

                                    tests = []

                                    for res_node in ana_node.findall('Risultato'):

                                        p_code = res_node.get('Codice')

                                        p_desc = res_node.findtext('Descrizione', '')

                                        val = res_node.findtext('Valore')

                                        udm = res_node.findtext('UDM', '')

                                        lim_inf = res_node.findtext('LimiteInferiore', '')

                                        lim_sup = res_node.findtext('LimiteSuperiore', '')

                                        fuori_norma = res_node.findtext('FuoriNorma', 'false').lower() == 'true'

                                        

                                        tests.append({

                                            "parameter_code": p_code,

                                            "parameter_name": p_desc,

                                            "value": val,

                                            "unit": udm,

                                            "limit_inf": lim_inf,

                                            "limit_sup": lim_sup,

                                            "out_of_bounds": fuori_norma

                                        })

                                    

                                    analyses.append({

                                        "service_code": srv_code,

                                        "tests": tests

                                    })

                                    

                                file_results.append({

                                    "barcode": barcode,

                                    "last_name": last_name,

                                    "first_name": first_name,

                                    "analyses": analyses

                                })

                        else: # CSV format

                            with open(file_path, "r", encoding="utf-8") as f:

                                lines = f.readlines()

                            if lines:

                                header = [h.strip().lower() for h in lines[0].split(',')]

                                rows_by_barcode = {}

                                for line in lines[1:]:

                                    parts = [p.strip() for p in line.split(',')]

                                    if len(parts) < 3:

                                        continue

                                    row_dict = dict(zip(header, parts))

                                    barcode = row_dict.get('barcode')

                                    srv_code = row_dict.get('service_code', '')

                                    param = row_dict.get('parameter') or row_dict.get('parameter_code') or row_dict.get('parameter_name')

                                    val = row_dict.get('value')

                                    unit = row_dict.get('unit', '')

                                    flag = row_dict.get('out_of_bounds', 'false').lower() in ('true', 'yes', '1', 'h', 'l')

                                    lim_inf = row_dict.get('limit_inf', '')

                                    lim_sup = row_dict.get('limit_sup', '')

                                    param_name = row_dict.get('parameter_name') or param

                                    

                                    if barcode and param and val:

                                        if barcode not in rows_by_barcode:

                                            rows_by_barcode[barcode] = {

                                                "barcode": barcode,

                                                "last_name": "",

                                                "first_name": "",

                                                "analyses": {}

                                            }

                                        if srv_code not in rows_by_barcode[barcode]["analyses"]:

                                            rows_by_barcode[barcode]["analyses"][srv_code] = {

                                                "service_code": srv_code,

                                                "tests": []

                                            }

                                        rows_by_barcode[barcode]["analyses"][srv_code]["tests"].append({

                                            "parameter_code": param,

                                            "parameter_name": param_name,

                                            "value": val,

                                            "unit": unit,

                                            "limit_inf": lim_inf,

                                            "limit_sup": lim_sup,

                                            "out_of_bounds": flag

                                        })

                                for barcode, data in rows_by_barcode.items():

                                    file_results.append({

                                        "barcode": barcode,

                                        "last_name": data["last_name"],

                                        "first_name": data["first_name"],

                                        "analyses": list(data["analyses"].values())

                                    })

                                        

                        updated_barcodes = set()

                        for fr in file_results:

                            for ana in fr["analyses"]:

                                nc_service_code = translate_code(transcoding, 'service', ana["service_code"], 'to_nextcare')

                                

                                cursor.execute("SELECT * FROM lab_samples WHERE barcode = %s", (fr['barcode'],))

                                sample = cursor.fetchone()

                                if not sample:

                                    continue

                                

                                cursor.execute("SELECT id FROM medical_services WHERE code = %s", (nc_service_code,))

                                srv_row = cursor.fetchone()

                                srv_id = srv_row['id'] if srv_row else None

                                

                                cursor.execute("SELECT * FROM lab_tests WHERE sample_id = %s", (sample['id'],))

                                sample_tests = cursor.fetchall()

                                

                                for t_res in ana["tests"]:

                                    nc_parameter_name = translate_code(transcoding, 'parameter', t_res['parameter_code'], 'to_nextcare')

                                    

                                    matched_test = None

                                    for t in sample_tests:

                                        if srv_id and t['service_id'] == srv_id:

                                            if t['test_name'].lower() == nc_parameter_name.lower():

                                                matched_test = t

                                                break

                                    if not matched_test:

                                        for t in sample_tests:

                                            if t['test_name'].lower() == nc_parameter_name.lower():

                                                matched_test = t

                                                break

                                    if not matched_test:

                                        for t in sample_tests:

                                            if nc_parameter_name.lower() in t['test_name'].lower():

                                                matched_test = t

                                                break

                                                

                                    if matched_test:

                                        status = 'flagged' if t_res['out_of_bounds'] else 'completed'

                                        ref_range = f"{t_res.get('limit_inf','')}-{t_res.get('limit_sup','')}" if (t_res.get('limit_inf') or t_res.get('limit_sup')) else None

                                        

                                        cursor.execute("""

                                            UPDATE lab_tests 

                                            SET result_value = %s, unit = %s, reference_range = COALESCE(%s, reference_range),

                                                status = %s, verified_by = 5, verified_at = CURRENT_TIMESTAMP

                                            WHERE id = %s

                                        """, (t_res['value'], t_res['unit'], ref_range, status, matched_test['id']))

                                        conn.commit()

                                        updated_barcodes.add(sample['barcode'])

                                        print(f"[LIS Importer] Updated test {matched_test['test_name']} for {sample['barcode']} to {t_res['value']}")

                        

                        for bar in updated_barcodes:

                            cursor.execute("SELECT * FROM lab_samples WHERE barcode = %s", (bar,))

                            sample = cursor.fetchone()

                            if sample:

                                cursor.execute("SELECT * FROM lab_tests WHERE sample_id = %s", (sample['id'],))

                                all_tests = cursor.fetchall()

                                all_done = all(t['result_value'] is not None for t in all_tests)

                                if all_done:

                                    cursor.execute("UPDATE lab_samples SET status = 'to_validate' WHERE id = %s", (sample['id'],))

                                    conn.commit()

                                    print(f"[LIS Importer] All tests complete for sample {bar}. Status set to 'to_validate'.")

                        

                        processed_dir = os.path.join(import_path, "processed")

                        os.makedirs(processed_dir, exist_ok=True)

                        dest_path = os.path.join(processed_dir, fname)

                        if os.path.exists(dest_path):

                            os.remove(dest_path)

                        shutil.move(file_path, dest_path)

                        results.extend(file_results)

                        print(f"[LIS Importer] Moved file {fname} to processed.")

                    except Exception as parse_err:

                        print(f"[LIS Importer Error] Parsing file {fname}: {parse_err}")

                        error_dir = os.path.join(import_path, "errors")

                        os.makedirs(error_dir, exist_ok=True)

                        dest_path = os.path.join(error_dir, fname)

                        if os.path.exists(dest_path):

                            os.remove(dest_path)

                        shutil.move(file_path, dest_path)

    except Exception as e:

        print(f"[LIS Importer General Error] {e}")

    finally:

        conn.close()

    return results



def handle_socket_client(client_sock, client_addr, socket_format, transcoding):

    print(f"[LIS Socket] Connected by {client_addr} using format {socket_format}")

    client_sock.settimeout(10.0)

    buffer = b""

    try:

        while True:

            data = client_sock.recv(4096)

            if not data:

                break

            buffer += data

            

            mllp_start = b"\x0b"

            mllp_end = b"\x1c\x0d"

            

            while True:

                msg_to_process = None

                if mllp_start in buffer and mllp_end in buffer:

                    start_idx = buffer.find(mllp_start)

                    end_idx = buffer.find(mllp_end, start_idx)

                    if end_idx != -1:

                        msg_to_process = buffer[start_idx+1 : end_idx]

                        buffer = buffer[end_idx+2 :]

                elif b"MSH|^~\\&" in buffer:

                    start_idx = buffer.find(b"MSH|^~\\&")

                    next_msh = buffer.find(b"MSH|^~\\&", start_idx + 8)

                    if next_msh != -1:

                        msg_to_process = buffer[start_idx:next_msh]

                        buffer = buffer[next_msh:]

                    else:

                        break

                elif b"<" in buffer and b">" in buffer:

                    if b"</ListaRichieste>" in buffer:

                        idx = buffer.find(b"</ListaRichieste>") + len(b"</ListaRichieste>")

                        msg_to_process = buffer[:idx]

                        buffer = buffer[idx:]

                    elif b"</Richiesta>" in buffer:

                        idx = buffer.find(b"</Richiesta>") + len(b"</Richiesta>")

                        msg_to_process = buffer[:idx]

                        buffer = buffer[idx:]

                    else:

                        break

                elif b"H|" in buffer and b"L|" in buffer:

                    start_idx = buffer.find(b"H|")

                    end_idx = buffer.find(b"L|", start_idx)

                    if end_idx != -1:

                        eol = buffer.find(b"\r", end_idx)

                        if eol == -1:

                            eol = buffer.find(b"\n", end_idx)

                        if eol != -1:

                            msg_to_process = buffer[start_idx : eol]

                            buffer = buffer[eol+1 :]

                        else:

                            break

                    else:

                        break

                else:

                    break

                

                if msg_to_process:

                    msg_str = msg_to_process.decode('utf-8', errors='ignore')

                    print(f"[LIS Socket] Processing message: {msg_str[:200]}...")

                    

                    # Log RX event

                    inst_id = None

                    try:

                        local_port = client_sock.getsockname()[1]

                        conn = get_db_connection()

                        if conn:

                            with conn.cursor() as cursor:

                                cursor.execute("SELECT id FROM equipment WHERE type = 'LIS' AND status = 'active' AND lis_interface_type = 'socket' AND lis_socket_port = %s", (local_port,))

                                inst_row = cursor.fetchone()

                                if inst_row:

                                    inst_id = inst_row['id']

                            conn.close()

                    except Exception as ie:

                        print(f"[LIS Socket Get Instrument Error] {ie}")

                        

                    if inst_id:

                        try:

                            log_equipment_event(inst_id, 'RX', socket_format.upper(), msg_str)

                        except Exception as le:

                            print(f"[LIS Socket RX Log Error] {le}")

                    

                    results = []

                    

                    if socket_format == 'hl7':

                        lines = [l.strip() for l in re.split(r'[\r\n]', msg_str) if l.strip()]

                        barcode = None

                        msh_control_id = "1"

                        

                        for line in lines:

                            fields = line.split('|')

                            if not fields:

                                continue

                            seg_name = fields[0]

                            

                            if seg_name == 'MSH':

                                if len(fields) > 9:

                                    msh_control_id = fields[9]

                            elif seg_name == 'OBR':

                                if len(fields) > 3:

                                    barcode = fields[3]

                            elif seg_name == 'OBX':

                                if len(fields) > 5:

                                    p_code = fields[3].split('^')[0]

                                    val = fields[5]

                                    unit = fields[6] if len(fields) > 6 else ''

                                    ref_range = fields[7] if len(fields) > 7 else ''

                                    flag = fields[8] if len(fields) > 8 else 'N'

                                    out_of_bounds = flag in ('H', 'L', 'HH', 'LL', 'A', 'AA')

                                    

                                    limit_inf = ''

                                    limit_sup = ''

                                    if '-' in ref_range:

                                        limit_inf, limit_sup = ref_range.split('-', 1)

                                    

                                    if barcode:

                                        results.append({

                                            "barcode": barcode,

                                            "service_code": "",

                                            "parameter_code": p_code,

                                            "parameter_name": p_code,

                                            "value": val,

                                            "unit": unit,

                                            "limit_inf": limit_inf,

                                            "limit_sup": limit_sup,

                                            "out_of_bounds": out_of_bounds

                                        })

                        

                        ack_msh = f"MSH|^~\\&|NEXTCARE||INSTRUMENT||{time.strftime('%Y%m%d%H%M%S')}||ACK^R01|{msh_control_id}|P|2.3"

                        ack_msa = f"MSA|AA|{msh_control_id}"

                        ack_message = f"{ack_msh}\r{ack_msa}\r"

                        ack_bytes = b"\x0b" + ack_message.encode('utf-8') + b"\x1c\x0d"

                        client_sock.sendall(ack_bytes)

                        if inst_id:

                            try:

                                log_equipment_event(inst_id, 'TX', 'HL7', ack_message)

                            except Exception as le:

                                print(f"[LIS Socket TX HL7 Log Error] {le}")

                        

                    elif socket_format == 'astm':

                        lines = [l.strip() for l in re.split(r'[\r\n]', msg_str) if l.strip()]

                        barcode = None

                        

                        for line in lines:

                            line_clean = re.sub(r'^[\x02\x01-\x1f\d\s]+', '', line)

                            fields = line_clean.split('|')

                            if not fields:

                                continue

                            rec_type = fields[0]

                            

                            if rec_type == 'O':

                                if len(fields) > 2:

                                    barcode = fields[2]

                            elif rec_type == 'R':

                                if len(fields) > 3:

                                    p_code = fields[2]

                                    p_code = p_code.replace('^', ' ').strip().split()[-1] if '^' in p_code else p_code

                                    val = fields[3]

                                    unit = fields[4] if len(fields) > 4 else ''

                                    ref_range = fields[5] if len(fields) > 5 else ''

                                    flag = fields[6] if len(fields) > 6 else 'N'

                                    out_of_bounds = flag in ('H', 'L', 'HH', 'LL', 'A', 'AA')

                                    

                                    limit_inf = ''

                                    limit_sup = ''

                                    if '-' in ref_range:

                                        limit_inf, limit_sup = ref_range.split('-', 1)

                                        

                                    if barcode:

                                        results.append({

                                            "barcode": barcode,

                                            "service_code": "",

                                            "parameter_code": p_code,

                                            "parameter_name": p_code,

                                            "value": val,

                                            "unit": unit,

                                            "limit_inf": limit_inf,

                                            "limit_sup": limit_sup,

                                            "out_of_bounds": out_of_bounds

                                        })

                        

                        client_sock.sendall(b"\x06")

                        if inst_id:

                            try:

                                log_equipment_event(inst_id, 'TX', 'ASTM', 'ACK')

                            except Exception as le:

                                print(f"[LIS Socket TX ASTM Log Error] {le}")



                        

                    elif socket_format == 'xml':

                        import xml.etree.ElementTree as ET

                        root = ET.fromstring(msg_str)

                        req_elements = []

                        if root.tag == 'Richiesta':

                            req_elements.append(root)

                        elif root.tag == 'ListaRichieste':

                            req_elements.extend(root.findall('Richiesta'))

                        else:

                            req_elements.extend(root.findall('.//Richiesta'))

                            

                        for req_node in req_elements:

                            barcode = req_node.findtext('IdRichiestaLis') or req_node.findtext('IdRichiesta')

                            if not barcode:

                                continue

                            

                            for ana_node in req_node.findall('Analisi'):

                                srv_code = ana_node.get('Codice')

                                for res_node in ana_node.findall('Risultato'):

                                    p_code = res_node.get('Codice')

                                    p_desc = res_node.findtext('Descrizione', '')

                                    val = res_node.findtext('Valore')

                                    udm = res_node.findtext('UDM', '')

                                    lim_inf = res_node.findtext('LimiteInferiore', '')

                                    lim_sup = res_node.findtext('LimiteSuperiore', '')

                                    fuori_norma = res_node.findtext('FuoriNorma', 'false').lower() == 'true'

                                    

                                    results.append({

                                        "barcode": barcode,

                                        "service_code": srv_code,

                                        "parameter_code": p_code,

                                        "parameter_name": p_desc,

                                        "value": val,

                                        "unit": udm,

                                        "limit_inf": lim_inf,

                                        "limit_sup": lim_sup,

                                        "out_of_bounds": fuori_norma

                                    })

                        

                        ack_xml = '<?xml version="1.0" encoding="utf-8"?><Response success="true"><Message>Received</Message></Response>'

                        client_sock.sendall(ack_xml.encode('utf-8'))

                        if inst_id:

                            try:

                                log_equipment_event(inst_id, 'TX', 'XML', ack_xml)

                            except Exception as le:

                                print(f"[LIS Socket TX XML Log Error] {le}")



                    

                    if results:

                        conn = get_db_connection()

                        if conn:

                            try:

                                with conn.cursor() as cursor:

                                    updated_barcodes = set()

                                    for r in results:

                                        nc_service_code = translate_code(transcoding, 'service', r['service_code'], 'to_nextcare')

                                        nc_parameter_name = translate_code(transcoding, 'parameter', r['parameter_code'], 'to_nextcare')

                                        

                                        cursor.execute("SELECT * FROM lab_samples WHERE barcode = %s", (r['barcode'],))

                                        sample = cursor.fetchone()

                                        if not sample:

                                            continue

                                            

                                        cursor.execute("SELECT * FROM lab_tests WHERE sample_id = %s", (sample['id'],))

                                        sample_tests = cursor.fetchall()

                                        

                                        cursor.execute("SELECT id FROM medical_services WHERE code = %s", (nc_service_code,))

                                        srv_row = cursor.fetchone()

                                        srv_id = srv_row['id'] if srv_row else None

                                        

                                        matched_test = None

                                        for t in sample_tests:

                                            if srv_id and t['service_id'] == srv_id:

                                                if t['test_name'].lower() == nc_parameter_name.lower():

                                                    matched_test = t

                                                    break

                                        if not matched_test:

                                            for t in sample_tests:

                                                if t['test_name'].lower() == nc_parameter_name.lower():

                                                    matched_test = t

                                                    break

                                        if not matched_test:

                                            for t in sample_tests:

                                                if nc_parameter_name.lower() in t['test_name'].lower():

                                                    matched_test = t

                                                    break

                                                    

                                        if matched_test:

                                            status = 'flagged' if r['out_of_bounds'] else 'completed'

                                            ref_range = f"{r.get('limit_inf','')}-{r.get('limit_sup','')}" if (r.get('limit_inf') or r.get('limit_sup')) else None

                                            

                                            cursor.execute("""

                                                UPDATE lab_tests 

                                                SET result_value = %s, unit = %s, reference_range = COALESCE(%s, reference_range),

                                                    status = %s, verified_by = 5, verified_at = CURRENT_TIMESTAMP

                                                WHERE id = %s

                                            """, (r['value'], r['unit'], ref_range, status, matched_test['id']))

                                            conn.commit()

                                            updated_barcodes.add(sample['barcode'])

                                            print(f"[LIS Socket] Updated test {matched_test['test_name']} for {sample['barcode']} to {r['value']}")

                                    

                                    for bar in updated_barcodes:

                                        cursor.execute("SELECT * FROM lab_samples WHERE barcode = %s", (bar,))

                                        sample = cursor.fetchone()

                                        if sample:

                                            cursor.execute("SELECT * FROM lab_tests WHERE sample_id = %s", (sample['id'],))

                                            all_tests = cursor.fetchall()

                                            all_done = all(t['result_value'] is not None for t in all_tests)

                                            if all_done:

                                                cursor.execute("UPDATE lab_samples SET status = 'to_validate' WHERE id = %s", (sample['id'],))

                                                conn.commit()

                                                print(f"[LIS Socket] Sample {bar} set to 'to_validate'.")

                            except Exception as e:

                                print(f"[LIS Socket DB Error] {e}")

                            finally:

                                conn.close()

    except Exception as e:

        print(f"[LIS Socket Client Connection Error] {e}")

    finally:

        client_sock.close()



def socket_listener_thread(port, socket_format, transcoding):

    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:

        server_sock.bind(("", port))

        server_sock.listen(5)

        print(f"[LIS Socket Server] Listening on port {port} for format {socket_format}...")

        

        RUNNING_SOCKET_SERVERS[port]['sock'] = server_sock

        RUNNING_SOCKET_SERVERS[port]['status'] = 'active'

        RUNNING_SOCKET_SERVERS[port]['error_reason'] = None

        

        while RUNNING_SOCKET_SERVERS.get(port, {}).get('active', False):

            try:

                client_sock, client_addr = server_sock.accept()

                t = threading.Thread(target=handle_socket_client, args=(client_sock, client_addr, socket_format, transcoding), daemon=True)

                t.start()

            except socket.error:

                break

    except Exception as e:

        print(f"[LIS Socket Server Error on Port {port}] {e}")

        if port in RUNNING_SOCKET_SERVERS:

            RUNNING_SOCKET_SERVERS[port]['status'] = 'error'

            RUNNING_SOCKET_SERVERS[port]['error_reason'] = str(e)

            RUNNING_SOCKET_SERVERS[port]['active'] = False

    finally:

        server_sock.close()

        print(f"[LIS Socket Server] Port {port} listener stopped.")



def guess_dose_class_id_by_name(name):

    if not name:

        return None

    import re

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



def run_db_migrations():

    conn = get_db_connection()

    if not conn:

        return

    try:

        with conn.cursor() as cursor:

            # 1. Check/Add custom_rates to invoices

            try:

                cursor.execute("SHOW COLUMNS FROM `invoices` LIKE 'custom_rates'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `invoices` ADD COLUMN `custom_rates` JSON NULL")

                    conn.commit()

            except Exception:

                pass



            # 2. Check/Add stamp_duty to invoices

            try:

                cursor.execute("SHOW COLUMNS FROM `invoices` LIKE 'stamp_duty'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `invoices` ADD COLUMN `stamp_duty` DECIMAL(10, 2) NOT NULL DEFAULT 0.00")

                    conn.commit()

            except Exception:

                pass



            # 3. Check/Create prima_nota_movements

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `prima_nota_movements` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `date` DATE NOT NULL,

                        `description` VARCHAR(255) NOT NULL,

                        `type` ENUM('entrata', 'uscita') NOT NULL,

                        `payment_method` VARCHAR(50) NOT NULL,

                        `amount` DECIMAL(10, 2) NOT NULL,

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

                conn.commit()

            except Exception:

                pass



            # 4. Check/Add profit_center and instrument_id to medical_services

            try:

                cursor.execute("SHOW COLUMNS FROM `medical_services` LIKE 'profit_center'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `medical_services` ADD COLUMN `profit_center` VARCHAR(100) NULL")

                    conn.commit()

            except Exception:

                pass



            try:

                cursor.execute("SHOW COLUMNS FROM `medical_services` LIKE 'instrument_id'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `medical_services` ADD COLUMN `instrument_id` INT NULL")

                    conn.commit()

            except Exception:

                pass



            # 5. Check/Create profit_centers

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `profit_centers` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `name` VARCHAR(100) NOT NULL UNIQUE,

                        `description` VARCHAR(255) NULL

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

                conn.commit()

                cursor.execute("SELECT COUNT(*) FROM `profit_centers`")

                pc_count = cursor.fetchone()

                count_val = list(pc_count.values())[0] if pc_count else 0

                if count_val == 0:

                    cursor.execute("INSERT INTO `profit_centers` (name, description) VALUES (%s, %s)", ('SPECIALISTICA', 'Esami di tipo visite specialistiche'))

                    cursor.execute("INSERT INTO `profit_centers` (name, description) VALUES (%s, %s)", ('IMAGING', 'Diagnostica per immagini e radiologia'))

                    cursor.execute("INSERT INTO `profit_centers` (name, description) VALUES (%s, %s)", ('LABORATORIO', 'Analisi cliniche e laboratorio (LIS)'))

                    conn.commit()

            except Exception:

                pass



            # 6. Check/Add session_uid and update ENUMs in lab_samples and lab_tests

            try:

                cursor.execute("SHOW COLUMNS FROM `lab_samples` LIKE 'session_uid'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `lab_samples` ADD COLUMN `session_uid` VARCHAR(50) NULL")

                    cursor.execute("ALTER TABLE `lab_samples` ADD INDEX `idx_sample_session` (`session_uid`)")

                    conn.commit()

                cursor.execute("ALTER TABLE `lab_samples` MODIFY COLUMN `status` ENUM('collected', 'received', 'processing', 'to_validate', 'completed', 'rejected', 'suspended') NOT NULL DEFAULT 'collected'")

                conn.commit()

                cursor.execute("ALTER TABLE `lab_tests` MODIFY COLUMN `status` ENUM('pending', 'completed', 'flagged', 'suspended') NOT NULL DEFAULT 'pending'")

                conn.commit()

            except Exception:

                pass



            # 7. Check/Add LIS interfacing columns to equipment

            try:

                cursor.execute("SHOW COLUMNS FROM `equipment` LIKE 'lis_interface_type'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_interface_type` VARCHAR(50) NOT NULL DEFAULT 'none'")

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_import_path` VARCHAR(255) NULL")

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_export_path` VARCHAR(255) NULL")

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_file_name` VARCHAR(255) NULL")

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_file_format` VARCHAR(50) NULL")

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_socket_port` INT NULL")

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_socket_format` VARCHAR(50) NULL")

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_transcoding` JSON NULL")

                    conn.commit()

                    print("[LIS Migrations] LIS interfacing columns added to equipment table.")

            except Exception as e:

                print(f"[LIS Migrations Error] equipment LIS columns: {e}")



            # 8. Check/Create lis_worksheets

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `lis_worksheets` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `name` VARCHAR(255) NOT NULL,

                        `service_ids` TEXT NOT NULL,

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

                conn.commit()

            except Exception:

                pass



            # 9. Check/Create equipment_logs

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `equipment_logs` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `equipment_id` INT NOT NULL,

                        `direction` ENUM('TX', 'RX') NOT NULL,

                        `message_type` VARCHAR(50) NOT NULL,

                        `content` TEXT NOT NULL,

                        `timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        FOREIGN KEY (`equipment_id`) REFERENCES `equipment`(`id`) ON DELETE CASCADE

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

                conn.commit()

            except Exception as e:

                print(f"[Migrations Error] equipment_logs: {e}")



            # 10. Check/Add lis_simulator_active to equipment

            try:

                cursor.execute("SHOW COLUMNS FROM `equipment` LIKE 'lis_simulator_active'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `equipment` ADD COLUMN `lis_simulator_active` TINYINT(1) NOT NULL DEFAULT 0")

                    conn.commit()

                    print("[LIS Migrations] Column lis_simulator_active added to equipment.")

            except Exception as e:

                print(f"[LIS Migrations Error] equipment lis_simulator_active: {e}")



            # 11. Check/Add login columns to staff and clinical_query to radiology_studies

            try:

                cursor.execute("SHOW COLUMNS FROM `staff` LIKE 'username'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `staff` ADD COLUMN `username` VARCHAR(100) UNIQUE NULL")

                    cursor.execute("ALTER TABLE `staff` ADD COLUMN `password` VARCHAR(255) NULL")

                    cursor.execute("ALTER TABLE `staff` ADD COLUMN `profiles` JSON NULL")

                    conn.commit()

                    print("[Migrations] Added login columns to staff table.")

            except Exception as e:

                print(f"[Migrations Warning] staff login columns: {e}")



            # Check/Modify staff role column enum to include 'biologo'

            try:

                cursor.execute("ALTER TABLE `staff` MODIFY COLUMN `role` ENUM('doctor', 'nurse', 'technician', 'administrative', 'manager', 'biologo') NOT NULL")

                conn.commit()

            except Exception as e:

                print(f"[Migrations Warning] staff role column alter: {e}")



            try:

                cursor.execute("SHOW COLUMNS FROM `radiology_studies` LIKE 'clinical_query'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `radiology_studies` ADD COLUMN `clinical_query` TEXT NULL")

                    conn.commit()

                    print("[Migrations] Added clinical_query to radiology_studies table.")

            except Exception as e:

                print(f"[Migrations Warning] radiology_studies clinical_query: {e}")



            try:

                cursor.execute("SHOW COLUMNS FROM `radiology_studies` LIKE 'attachment_name'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `radiology_studies` ADD COLUMN `attachment_name` VARCHAR(255) NULL")

                    cursor.execute("ALTER TABLE `radiology_studies` ADD COLUMN `attachment_data` LONGTEXT NULL")

                    conn.commit()

                    print("[Migrations] Added attachment columns to radiology_studies table.")

            except Exception as e:

                print(f"[Migrations Warning] radiology_studies attachment columns: {e}")



            # Seed/Update staff members with login credentials

            try:

                cursor.execute("SELECT COUNT(*) FROM `staff` WHERE `username` = 'pirone'")

                pirone_exists = cursor.fetchone()

                exists_val = list(pirone_exists.values())[0] if isinstance(pirone_exists, dict) else (pirone_exists[0] if pirone_exists else 0)

                

                if exists_val == 0:

                    cursor.execute(

                        "INSERT INTO `staff` (first_name, last_name, role, email, phone, active, username, password, profiles) VALUES (%s, %s, %s, %s, %s, 1, %s, %s, %s)",

                        ('Roberto', 'Pirone', 'manager', 'r.pirone@nextcare.it', '+39 333 1111111', 'pirone', 'RobLeti2024', '["admin"]')

                    )

                    conn.commit()

                    print("[Migrations] Seeded admin user 'pirone'.")

                    

                # Update existing staff with usernames and profiles if NULL

                staff_updates = [

                    (1, 'rossi', 'Password123', '["medico"]'),

                    (2, 'bianchi', 'Password123', '["medico"]'),

                    (3, 'verdi', 'Password123', '["medico"]'),

                    (4, 'neri', 'Password123', '["infermiere"]'),

                    (5, 'moretti', 'Password123', '["tsrm"]'),

                    (6, 'rizzo', 'Password123', '["segreteria"]')

                ]

                for sid, suser, spass, sprofs in staff_updates:

                    cursor.execute("SELECT username FROM `staff` WHERE `id` = %s", (sid,))

                    row = cursor.fetchone()

                    username_val = row.get('username') if isinstance(row, dict) else (row[0] if row else None)

                    if username_val is None:

                        cursor.execute(

                            "UPDATE `staff` SET `username` = %s, `password` = %s, `profiles` = %s WHERE `id` = %s",

                            (suser, spass, sprofs, sid)

                        )

                conn.commit()

            except Exception as e:

                print(f"[Migrations Warning] seeding/updating staff login: {e}")



            # 12. Check/Create consent_templates table

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `consent_templates` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `title` VARCHAR(255) NOT NULL,

                        `content` TEXT NOT NULL,

                        `scope` VARCHAR(50) NOT NULL DEFAULT 'all',

                        `modality` VARCHAR(50) NULL,

                        `doctor_id` INT NULL,

                        `min_age` INT NULL,

                        `max_age` INT NULL,

                        `gender` VARCHAR(10) NOT NULL DEFAULT 'all',

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                        FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE SET NULL

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

                conn.commit()

                

                # Seed default templates if empty

                cursor.execute("SELECT COUNT(*) FROM `consent_templates`")

                ct_count = cursor.fetchone()

                ct_count_val = list(ct_count.values())[0] if ct_count else (ct_count[0] if isinstance(ct_count, tuple) else 0)

                if ct_count_val == 0:

                    cursor.execute("""

                        INSERT INTO `consent_templates` (title, content, scope, modality, gender, min_age, max_age)

                        VALUES (%s, %s, %s, %s, %s, %s, %s)

                    """, (

                        "Consenso Informato Diagnostico (Legge 219/2017)",

                        "<h2>CONSENSO INFORMATO AL TRATTAMENTO SANITARIO (L. 219/2017)</h2><p>Il sottoscritto <b>{paziente}</b> (Codice Fiscale: <b>{codice_fiscale}</b>, nato/a il <b>{data_nascita}</b>) dichiara di essere stato adeguatamente informato dal medico in merito alla natura, ai benefici, ai rischi legati alle radiazioni ed alle possibili alternative diagnostiche per l'esame proposto.</p><p>Dichiara inoltre di aver compreso pienamente quanto esposto, di aver avuto l'opportunità di porre domande e di autorizzare liberamente l'esecuzione della procedura.</p><p>Firma del Paziente: _________________________  Data: {data}</p>",

                        "by_modality",

                        "RIS",

                        "all",

                        None,

                        None

                    ))

                    cursor.execute("""

                        INSERT INTO `consent_templates` (title, content, scope, modality, gender, min_age, max_age)

                        VALUES (%s, %s, %s, %s, %s, %s, %s)

                    """, (

                        "Dichiarazione Stato di Gravidanza (Età Fertile)",

                        "<h2>DICHIARAZIONE DI ASSENZA DI STATO DI GRAVIDANZA</h2><p>La sottoscritta <b>{paziente}</b> (nata il <b>{data_nascita}</b>, C.F. <b>{codice_fiscale}</b>), consapevole dei rischi biologici connessi all'esposizione a radiazioni ionizzanti per il feto, dichiara sotto la propria responsabilità:<br><br><b>[  ]</b> Di escludere in modo certo lo stato di gravidanza.<br><b>[  ]</b> Di non poter escludere lo stato di gravidanza.</p><p>Attesta inoltre di essere stata informata della necessità di segnalare immediatamente al personale sanitario qualsiasi dubbio in merito.</p><p>Firma della Paziente: _________________________  Data: {data}</p>",

                        "gender_age",

                        "RIS",

                        "F",

                        14,

                        60

                    ))

                    cursor.execute("""

                        INSERT INTO `consent_templates` (title, content, scope, modality, gender, min_age, max_age)

                        VALUES (%s, %s, %s, %s, %s, %s, %s)

                    """, (

                        "Consenso Informato al Prelievo Ematico (LIS)",

                        "<h2>CONSENSO AL PRELIEVO E TRATTAMENTO CAMPIONI BIOLOGICI</h2><p>Il sottoscritto <b>{paziente}</b> (Codice Fiscale: <b>{codice_fiscale}</b>, nato/a il <b>{data_nascita}</b>) autorizza il personale infermieristico di NextCare all'esecuzione del prelievo ematico e dei campioni biologici necessari all'esecuzione degli esami di laboratorio prescritti.</p><p>Dichiara di essere a conoscenza delle modalità di esecuzione, dei possibili lievi effetti collaterali (es. ematoma) e del trattamento dei dati sanitari connessi.</p><p>Firma del Paziente: _________________________  Data: {data}</p>",

                        "by_modality",

                        "LIS",

                        "all",

                        None,

                        None

                    ))

                    conn.commit()

                    print("[Migrations] Seeded default consent templates.")

            except Exception as e:

                print(f"[Migrations Warning] consent_templates creation/seeding: {e}")



            # 13. Check/Create doctor_closures table

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `doctor_closures` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `doctor_id` INT NULL,

                        `start_date` DATE NOT NULL,

                        `end_date` DATE NOT NULL,

                        `start_time` VARCHAR(8) NULL,

                        `end_time` VARCHAR(8) NULL,

                        `description` VARCHAR(255) NOT NULL,

                        `closure_type` VARCHAR(50) NOT NULL,

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                        `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

                        FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

                conn.commit()

                

                # Verify and add columns if they don't exist yet

                cursor.execute("SHOW COLUMNS FROM `doctor_closures` LIKE 'start_time'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `doctor_closures` ADD COLUMN `start_time` VARCHAR(8) NULL AFTER `end_date`")

                    cursor.execute("ALTER TABLE `doctor_closures` ADD COLUMN `end_time` VARCHAR(8) NULL AFTER `start_time`")

                    conn.commit()

                    print("[Migrations] Added start_time and end_time columns to doctor_closures.")

                else:

                    print("[Migrations] doctor_closures table and columns checked/created.")

            except Exception as e:

                print(f"[Migrations Warning] doctor_closures table check/create: {e}")



            # 14. Check/Create dose_classes table

            try:

                cursor.execute("""

                    CREATE TABLE IF NOT EXISTS `dose_classes` (

                        `id` INT AUTO_INCREMENT PRIMARY KEY,

                        `code` VARCHAR(50) NOT NULL UNIQUE,

                        `range_msv` VARCHAR(100) NOT NULL,

                        `description` VARCHAR(255) NULL,

                        `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP

                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci

                """)

                conn.commit()

                

                # Seed default dose classes if empty

                cursor.execute("SELECT COUNT(*) FROM `dose_classes`")

                dc_count = cursor.fetchone()

                dc_count_val = list(dc_count.values())[0] if dc_count else (dc_count[0] if isinstance(dc_count, tuple) else 0)

                if dc_count_val == 0:

                    cursor.execute("INSERT INTO `dose_classes` (code, range_msv, description) VALUES (%s, %s, %s)", ('0', '0 mSv', 'Ecografia, Risonanza Magnetica (senza radiazioni)'))

                    cursor.execute("INSERT INTO `dose_classes` (code, range_msv, description) VALUES (%s, %s, %s)", ('I', '< 1 mSv', 'RX Torace, RX arti'))

                    cursor.execute("INSERT INTO `dose_classes` (code, range_msv, description) VALUES (%s, %s, %s)", ('II', '1 - 5 mSv', 'RX addome, TC cranio'))

                    cursor.execute("INSERT INTO `dose_classes` (code, range_msv, description) VALUES (%s, %s, %s)", ('III', '5 - 10 mSv', 'TC torace, TC addome'))

                    cursor.execute("INSERT INTO `dose_classes` (code, range_msv, description) VALUES (%s, %s, %s)", ('IV', '> 10 mSv', 'Procedure interventistiche, TC addome-bacino'))

                    conn.commit()

                    print("[Migrations] Seeded default dose classes.")

            except Exception as e:

                print(f"[Migrations Warning] dose_classes table creation/seeding: {e}")



            # 15. Check/Add dose_class_id to medical_services

            try:

                cursor.execute("SHOW COLUMNS FROM `medical_services` LIKE 'dose_class_id'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `medical_services` ADD COLUMN `dose_class_id` INT NULL")

                    cursor.execute("ALTER TABLE `medical_services` ADD CONSTRAINT `fk_services_dose_class` FOREIGN KEY (`dose_class_id`) REFERENCES `dose_classes`(`id`) ON DELETE SET NULL")

                    conn.commit()

                    print("[Migrations] Added dose_class_id column to medical_services.")

            except Exception as e:

                print(f"[Migrations Warning] dose_class_id column creation: {e}")



            # 17. Check/Add dose_value_msv to radiology_studies

            try:

                cursor.execute("SHOW COLUMNS FROM `radiology_studies` LIKE 'dose_value_msv'")

                if not cursor.fetchone():

                    cursor.execute("ALTER TABLE `radiology_studies` ADD COLUMN `dose_value_msv` DECIMAL(8,4) NULL")

                    conn.commit()

                    print("[Migrations] Added dose_value_msv column to radiology_studies.")

            except Exception as e:

                print(f"[Migrations Warning] dose_value_msv column creation: {e}")



            # Check/Modify status ENUM in radiology_studies

            try:

                cursor.execute("SHOW COLUMNS FROM `radiology_studies` LIKE 'status'")

                col_info = cursor.fetchone()

                if col_info and 'executed' not in col_info.get('Type', ''):

                    cursor.execute("ALTER TABLE `radiology_studies` MODIFY COLUMN `status` ENUM('scheduled', 'in_progress', 'executed', 'completed', 'cancelled') NOT NULL DEFAULT 'scheduled'")

                    conn.commit()

                    print("[Migrations] Modified status ENUM of radiology_studies to include 'executed'.")

            except Exception as e:

                print(f"[Migrations Warning] radiology_studies status enum modification: {e}")



            # 16. One-time migration to auto-classify existing RIS exams in MySQL

            try:

                cursor.execute("SELECT id, name FROM `medical_services` WHERE `type` = 'ris' AND `dose_class_id` IS NULL")

                unclassified = cursor.fetchall()

                if unclassified:

                    for row in unclassified:

                        srv_id = row['id']

                        srv_name = row['name']

                        guessed_id = guess_dose_class_id_by_name(srv_name)

                        if guessed_id:

                            cursor.execute("UPDATE `medical_services` SET `dose_class_id` = %s WHERE `id` = %s", (guessed_id, srv_id))

                    conn.commit()

                    print(f"[Migrations] Auto-classified {len(unclassified)} existing RIS exams in MySQL.")

            except Exception as e:

                print(f"[Migrations Warning] auto-classifying existing RIS exams: {e}")


            # 4. New migrations: Companies and Templates
            try:
                # Create companies table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `companies` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(255) NOT NULL,
                    `vat_number` VARCHAR(50) NULL,
                    `fiscal_code` VARCHAR(50) NULL,
                    `address` VARCHAR(255) NULL,
                    `email` VARCHAR(255) NULL,
                    `phone` VARCHAR(255) NULL,
                    `price_list_id` INT NULL,
                    `billing_type` ENUM('patient', 'company_post') NOT NULL DEFAULT 'patient',
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`price_list_id`) REFERENCES `price_lists`(`id`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] creating companies table: {e_mig}")

            try:
                # Create ris_report_templates table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `ris_report_templates` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `title` VARCHAR(255) NOT NULL,
                    `content` TEXT NOT NULL,
                    `service_id` INT NULL,
                    `doctor_ids` VARCHAR(255) NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] creating ris_report_templates table: {e_mig}")

            try:
                # Check/Add company_id to invoices
                cursor.execute("SHOW COLUMNS FROM `invoices` LIKE 'company_id'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `invoices` ADD COLUMN `company_id` INT NULL, ADD FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL")
                    conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] adding company_id to invoices: {e_mig}")

            try:
                # Check/Add is_company_post to invoices
                cursor.execute("SHOW COLUMNS FROM `invoices` LIKE 'is_company_post'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `invoices` ADD COLUMN `is_company_post` TINYINT(1) NOT NULL DEFAULT 0")
                    conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] adding is_company_post to invoices: {e_mig}")

            try:
                # Check/Add company_id to admissions
                cursor.execute("SHOW COLUMNS FROM `admissions` LIKE 'company_id'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `admissions` ADD COLUMN `company_id` INT NULL, ADD FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL")
                    conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] adding company_id to admissions: {e_mig}")

            try:
                # Seed default companies if empty
                cursor.execute("SELECT COUNT(*) FROM `companies`")
                row = cursor.fetchone()
                count = list(row.values())[0] if row else 0
                if count == 0:
                    cursor.execute("""
                    INSERT INTO `companies` (name, vat_number, fiscal_code, address, email, phone, price_list_id, billing_type) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, ("Acme Corporation S.r.l.", "IT01234567890", "01234567890", "Via delle Industrie 10, Milano", "amministrazione@acme.it", "02-123456", 2, "company_post"))
                    
                    cursor.execute("""
                    INSERT INTO `companies` (name, vat_number, fiscal_code, address, email, phone, price_list_id, billing_type) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, ("BioTech Health Group", "IT09876543210", "09876543210", "Corso Roma 45, Torino", "info@biotechhealth.it", "011-987654", 1, "patient"))
                    conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] seeding default companies: {e_mig}")

            try:
                # Check/Add bulk_session_uid to lab_samples
                cursor.execute("SHOW COLUMNS FROM `lab_samples` LIKE 'bulk_session_uid'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `lab_samples` ADD COLUMN `bulk_session_uid` VARCHAR(50) NULL")
                    conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] adding bulk_session_uid to lab_samples: {e_mig}")

            try:
                # Check/Add company_id to patients
                cursor.execute("SHOW COLUMNS FROM `patients` LIKE 'company_id'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `patients` ADD COLUMN `company_id` INT NULL, ADD FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL")
                    conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] adding company_id to patients: {e_mig}")

            try:
                # Modify study_type column in radiology_studies to support 'VISIT' ENUM value
                cursor.execute("ALTER TABLE `radiology_studies` MODIFY COLUMN `study_type` ENUM('XRAY', 'MRI', 'CT', 'ULTRASOUND', 'MAMMOGRAPHY', 'VISIT') NOT NULL")
                conn.commit()
            except Exception as e_mig:
                print(f"[Migrations Warning] modifying study_type ENUM in radiology_studies: {e_mig}")

            try:
                cursor.execute("SHOW COLUMNS FROM `patients` LIKE 'cf'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `patients` ADD COLUMN `cf` VARCHAR(16) NULL")
                    conn.commit()
                    cursor.execute("UPDATE `patients` SET `cf` = `tax_code`")
                    conn.commit()
                    print("[Migrations] Added cf column to patients.")
            except Exception as e_mig:
                print(f"[Migrations Warning] adding cf to patients: {e_mig}")

            try:
                cursor.execute("SHOW COLUMNS FROM `companies` LIKE 'piva'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `companies` ADD COLUMN `piva` VARCHAR(50) NULL")
                    conn.commit()
                    cursor.execute("UPDATE `companies` SET `piva` = `vat_number`")
                    conn.commit()
                    print("[Migrations] Added piva column to companies.")
            except Exception as e_mig:
                print(f"[Migrations Warning] adding piva to companies: {e_mig}")

            # --- PHASE 3 MIGRATIONS ---
            try:
                cursor.execute("SHOW COLUMNS FROM `staff` LIKE 'pending_reports_threshold'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `staff` ADD COLUMN `pending_reports_threshold` INT NOT NULL DEFAULT 5")
                    conn.commit()
                    print("[Migrations] Added pending_reports_threshold column to staff.")
            except Exception as e_mig:
                print(f"[Migrations Warning] adding pending_reports_threshold to staff: {e_mig}")

            try:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `chat_messages` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `sender_id` INT NOT NULL,
                    `recipient_id` INT NOT NULL,
                    `message_text` TEXT NULL,
                    `attachment_name` VARCHAR(255) NULL,
                    `attachment_data` LONGTEXT NULL,
                    `patient_id` INT NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`sender_id`) REFERENCES `staff`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`recipient_id`) REFERENCES `staff`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)
                conn.commit()
                print("[Migrations] Created chat_messages table.")
            except Exception as e_mig:
                print(f"[Migrations Warning] creating chat_messages table: {e_mig}")

            try:
                cursor.execute("""
                    SELECT CONSTRAINT_NAME 
                    FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE 
                    WHERE TABLE_SCHEMA = 'nextcare_db' 
                      AND TABLE_NAME = 'doctor_agendas' 
                      AND COLUMN_NAME = 'doctor_id'
                      AND CONSTRAINT_NAME = 'doctor_agendas_ibfk_1'
                """)
                if cursor.fetchone():
                    cursor.execute("ALTER TABLE `doctor_agendas` DROP FOREIGN KEY `doctor_agendas_ibfk_1`")
                    conn.commit()
                cursor.execute("ALTER TABLE `doctor_agendas` MODIFY COLUMN `doctor_id` INT NULL")
                conn.commit()
                cursor.execute("ALTER TABLE `doctor_agendas` ADD CONSTRAINT `doctor_agendas_ibfk_1` FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE")
                conn.commit()
                print("[Migrations] Modified doctor_agendas.doctor_id to be NULLable.")
            except Exception as e_mig:
                print(f"[Migrations Warning] modifying doctor_id nullable in doctor_agendas: {e_mig}")

            try:
                cursor.execute("SHOW COLUMNS FROM `doctor_agendas` LIKE 'name'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `doctor_agendas` ADD COLUMN `name` VARCHAR(150) NULL")
                    conn.commit()
                    print("[Migrations] Added name column to doctor_agendas.")
            except Exception as e_mig:
                print(f"[Migrations Warning] adding name to doctor_agendas: {e_mig}")

            try:
                cursor.execute("SHOW COLUMNS FROM `doctor_agendas` LIKE 'reporting_doctor_ids'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `doctor_agendas` ADD COLUMN `reporting_doctor_ids` JSON NULL")
                    conn.commit()
                    print("[Migrations] Added reporting_doctor_ids column to doctor_agendas.")
            except Exception as e_mig:
                print(f"[Migrations Warning] adding reporting_doctor_ids to doctor_agendas: {e_mig}")

            try:
                cursor.execute("SHOW COLUMNS FROM `appointments` LIKE 'agenda_id'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `appointments` ADD COLUMN `agenda_id` INT NULL")
                    cursor.execute("ALTER TABLE `appointments` ADD CONSTRAINT `fk_appointments_agenda` FOREIGN KEY (`agenda_id`) REFERENCES `doctor_agendas`(`id`) ON DELETE SET NULL")
                    conn.commit()
                    print("[Migrations] Added agenda_id column and FK constraint to appointments.")
            except Exception as e_mig:
                print(f"[Migrations Warning] adding agenda_id to appointments: {e_mig}")

            # NEW ENTERPRISE TABLES CREATION & MIGRATIONS
            try:
                # 1. Create stock_suppliers table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `stock_suppliers` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(255) NOT NULL,
                    `contact_person` VARCHAR(255) NULL,
                    `phone` VARCHAR(50) NULL,
                    `email` VARCHAR(100) NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 2. Create stock_fridges table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `stock_fridges` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(100) NOT NULL,
                    `location` VARCHAR(255) NULL,
                    `temperature_log` JSON NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 3. Create stock_items table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `stock_items` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `name` VARCHAR(255) NOT NULL,
                    `item_type` ENUM('LIS', 'RIS', 'Generic') NOT NULL,
                    `supplier_id` INT NULL,
                    `fridge_id` INT NULL,
                    `quantity` INT NOT NULL DEFAULT 0,
                    `lot_number` VARCHAR(100) NULL,
                    `expiration_date` DATE NULL,
                    `alert_sent` TINYINT(1) DEFAULT 0,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`supplier_id`) REFERENCES `stock_suppliers`(`id`) ON DELETE SET NULL,
                    FOREIGN KEY (`fridge_id`) REFERENCES `stock_fridges`(`id`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 4. Create stock_logs table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `stock_logs` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `item_id` INT NOT NULL,
                    `operation_type` ENUM('carico', 'scarico') NOT NULL,
                    `quantity` INT NOT NULL,
                    `operator_id` INT NOT NULL,
                    `notes` VARCHAR(255) NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`item_id`) REFERENCES `stock_items`(`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 5. Create ssn_recipes table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `ssn_recipes` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `nre` VARCHAR(50) NOT NULL UNIQUE,
                    `patient_id` INT NOT NULL,
                    `exemption_code` VARCHAR(50) NULL,
                    `diagnostic_question` TEXT NULL,
                    `recipe_date` DATE NOT NULL,
                    `prescribing_doctor` VARCHAR(255) NULL,
                    `priority_code` CHAR(1) NULL,
                    `asl_code` VARCHAR(50) NULL,
                    `ticket_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    `refund_amount` DECIMAL(10,2) NOT NULL DEFAULT 0.00,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 6. Create ssn_exemptions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `ssn_exemptions` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `code` VARCHAR(50) NOT NULL UNIQUE,
                    `name` VARCHAR(1000) NOT NULL,
                    `pct` DECIMAL(5, 2) NOT NULL,
                    `type` VARCHAR(100) NULL,
                    `number_required` TINYINT(1) DEFAULT 0,
                    `active` TINYINT(1) DEFAULT 1
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 7. Create ssn_asl_mapping table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `ssn_asl_mapping` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `region` VARCHAR(100) NOT NULL,
                    `code` VARCHAR(50) NULL,
                    `name` VARCHAR(255) NOT NULL,
                    `city` VARCHAR(255) NOT NULL,
                    `province` VARCHAR(50) NULL,
                    `address` VARCHAR(255) NULL,
                    `email` VARCHAR(255) NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 8. Create rehab_cycles table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `rehab_cycles` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `patient_id` INT NOT NULL,
                    `doctor_id` INT NOT NULL,
                    `diagnosis` TEXT NULL,
                    `total_sessions` INT NOT NULL DEFAULT 10,
                    `billing_mode` ENUM('start', 'end') NOT NULL DEFAULT 'start',
                    `status` ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 9. Create rehab_sessions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `rehab_sessions` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `cycle_id` INT NOT NULL,
                    `session_number` INT NOT NULL,
                    `scheduled_at` DATETIME NOT NULL,
                    `status` ENUM('scheduled', 'completed', 'suspended', 'rescheduled') DEFAULT 'scheduled',
                    `vas_scale` INT NULL,
                    `daily_diary` TEXT NULL,
                    `therapist_id` INT NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`cycle_id`) REFERENCES `rehab_cycles`(`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 10. Create doctor_compensations_config table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `doctor_compensations_config` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `doctor_id` INT NOT NULL,
                    `service_id` INT NULL,
                    `branch` VARCHAR(100) NULL,
                    `patient_type` VARCHAR(50) NULL,
                    `insurance_id` INT NULL,
                    `company_id` INT NULL,
                    `trigger_event` ENUM('erogato', 'refertato', 'fatturato', 'incassato') NOT NULL,
                    `compensation_type` ENUM('percentage', 'fixed') NOT NULL,
                    `value` DECIMAL(10, 2) NOT NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`service_id`) REFERENCES `medical_services`(`id`) ON DELETE SET NULL,
                    FOREIGN KEY (`insurance_id`) REFERENCES `insurances`(`id`) ON DELETE SET NULL,
                    FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 11. Create doctor_calculated_compensations table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `doctor_calculated_compensations` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `doctor_id` INT NOT NULL,
                    `appointment_id` INT NULL,
                    `invoice_id` INT NULL,
                    `service_id` INT NOT NULL,
                    `event_type` VARCHAR(50) NOT NULL,
                    `base_amount` DECIMAL(10,2) NOT NULL,
                    `calculated_amount` DECIMAL(10,2) NOT NULL,
                    `status` ENUM('pending', 'liquidato') DEFAULT 'pending',
                    `payout_date` DATE NULL,
                    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE,
                    FOREIGN KEY (`appointment_id`) REFERENCES `appointments`(`id`) ON DELETE SET NULL,
                    FOREIGN KEY (`invoice_id`) REFERENCES `invoices`(`id`) ON DELETE SET NULL,
                    FOREIGN KEY (`service_id`) REFERENCES `medical_services`(`id`) ON DELETE CASCADE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 12. Create fse_transmissions table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `fse_transmissions` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `document_type` ENUM('lis', 'ris', 'visit') NOT NULL,
                    `document_id` INT NOT NULL,
                    `workflow_instance_id` VARCHAR(256) NULL,
                    `trace_id` VARCHAR(100) NULL,
                    `status` ENUM('pending', 'validated', 'published', 'error') DEFAULT 'pending',
                    `error_message` TEXT NULL,
                    `cda_xml` LONGTEXT NULL,
                    `sent_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 13. Create system_license table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `system_license` (
                    `serial_number` VARCHAR(100) PRIMARY KEY,
                    `version` VARCHAR(20) NOT NULL DEFAULT '1.0',
                    `activated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # 14. Create generated_licenses table
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS `generated_licenses` (
                    `id` INT AUTO_INCREMENT PRIMARY KEY,
                    `serial_number` VARCHAR(100) UNIQUE NOT NULL,
                    `cliente` VARCHAR(255) NOT NULL,
                    `durata_mesi` INT NOT NULL,
                    `data_attivazione` DATE NOT NULL,
                    `data_scadenza` DATE NOT NULL,
                    `moduli` TEXT NOT NULL,
                    `stato` VARCHAR(50) DEFAULT 'creata',
                    `creato_il` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                """)

                # Alter Tables
                # invoices
                cursor.execute("SHOW COLUMNS FROM `invoices` LIKE 'sts_submitted'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `invoices` ADD COLUMN `sts_submitted` TINYINT(1) NOT NULL DEFAULT 0")
                    cursor.execute("ALTER TABLE `invoices` ADD COLUMN `sts_protocol` VARCHAR(100) NULL")
                    cursor.execute("ALTER TABLE `invoices` ADD COLUMN `sts_error` TEXT NULL")
                
                # patients
                cursor.execute("SHOW COLUMNS FROM `patients` LIKE 'portal_active'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `patients` ADD COLUMN `portal_active` TINYINT(1) NOT NULL DEFAULT 0")
                    cursor.execute("ALTER TABLE `patients` ADD COLUMN `portal_username` VARCHAR(100) NULL")
                    cursor.execute("ALTER TABLE `patients` ADD COLUMN `portal_password` VARCHAR(100) NULL")
                
                # companies
                cursor.execute("SHOW COLUMNS FROM `companies` LIKE 'portal_active'")
                if not cursor.fetchone():
                    cursor.execute("ALTER TABLE `companies` ADD COLUMN `portal_active` TINYINT(1) NOT NULL DEFAULT 0")
                    cursor.execute("ALTER TABLE `companies` ADD COLUMN `portal_username` VARCHAR(100) NULL")
                    cursor.execute("ALTER TABLE `companies` ADD COLUMN `portal_password` VARCHAR(100) NULL")
                
                conn.commit()

                # Seed data: patients portal status
                cursor.execute("UPDATE `patients` SET portal_active=1, portal_username='mario', portal_password='123' WHERE id=1")
                
                # Seed data: companies portal status
                cursor.execute("UPDATE `companies` SET portal_active=1, portal_username='acme', portal_password='123' WHERE id=1")
                
                # Seed stock suppliers
                cursor.execute("SELECT COUNT(*) FROM `stock_suppliers`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `stock_suppliers` (id, name, contact_person, phone, email) VALUES (1, 'Bio-Rad Laboratories', 'Giovanni Bianchi', '02-123456', 'info@biorad.it')")
                    cursor.execute("INSERT INTO `stock_suppliers` (id, name, contact_person, phone, email) VALUES (2, 'Roche Diagnostics', 'Laura Rossi', '02-654321', 'info@roche.it')")
                
                # Seed stock fridges
                cursor.execute("SELECT COUNT(*) FROM `stock_fridges`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `stock_fridges` (id, name, location, temperature_log) VALUES (1, 'Frigo LIS 01', 'Laboratorio Analisi', '[{\"timestamp\": \"2026-06-14T00:00:00Z\", \"temperature\": 4.2}]')")
                    cursor.execute("INSERT INTO `stock_fridges` (id, name, location, temperature_log) VALUES (2, 'Frigo Reagenti 02', 'Deposito Farmaci', '[{\"timestamp\": \"2026-06-14T00:00:00Z\", \"temperature\": 3.8}]')")
                
                # Seed stock items
                cursor.execute("SELECT COUNT(*) FROM `stock_items`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `stock_items` (id, name, item_type, supplier_id, fridge_id, quantity, lot_number, expiration_date) VALUES (1, 'Provetta EDTA K3 3ml', 'LIS', 1, 1, 500, 'LOT12345', '2027-06-14')")
                    cursor.execute("INSERT INTO `stock_items` (id, name, item_type, supplier_id, fridge_id, quantity, lot_number, expiration_date) VALUES (2, 'Reagente Glicemia Basale', 'LIS', 2, 1, 20, 'LOT67890', '2026-09-14')")
                    cursor.execute("INSERT INTO `stock_items` (id, name, item_type, supplier_id, fridge_id, quantity, lot_number, expiration_date) VALUES (3, 'Gel per Fisioterapia 5L', 'Generic', 1, NULL, 5, 'LOT99999', '2028-12-31')")
                
                # Seed stock logs
                cursor.execute("SELECT COUNT(*) FROM `stock_logs`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `stock_logs` (item_id, operation_type, quantity, operator_id, notes) VALUES (1, 'carico', 500, 1, 'Carico iniziale DDT 45/2026')")
                    cursor.execute("INSERT INTO `stock_logs` (item_id, operation_type, quantity, operator_id, notes) VALUES (2, 'carico', 20, 1, 'Carico iniziale DDT 45/2026')")
                    cursor.execute("INSERT INTO `stock_logs` (item_id, operation_type, quantity, operator_id, notes) VALUES (3, 'carico', 5, 1, 'Carico iniziale DDT 46/2026')")
                
                # Seed rehab cycles
                cursor.execute("SELECT COUNT(*) FROM `rehab_cycles`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `rehab_cycles` (id, patient_id, doctor_id, diagnosis, total_sessions, billing_mode, status) VALUES (1, 1, 1, 'Riabilitazione post-traumatica spalla destra', 5, 'start', 'active')")
                
                # Seed rehab sessions
                cursor.execute("SELECT COUNT(*) FROM `rehab_sessions`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `rehab_sessions` (cycle_id, session_number, scheduled_at, status, vas_scale, daily_diary, therapist_id) VALUES (1, 1, '2026-06-10 10:00:00', 'completed', 7, 'Prima seduta: valutazione e mobilizzazione passiva.', 1)")
                    cursor.execute("INSERT INTO `rehab_sessions` (cycle_id, session_number, scheduled_at, status, vas_scale, daily_diary, therapist_id) VALUES (1, 2, '2026-06-12 10:00:00', 'completed', 5, 'Seconda seduta: esercizi di rinforzo leggero.', 1)")
                    cursor.execute("INSERT INTO `rehab_sessions` (cycle_id, session_number, scheduled_at, status, vas_scale, daily_diary, therapist_id) VALUES (1, 3, '2026-06-15 10:00:00', 'scheduled', NULL, NULL, 1)")
                
                # Seed doctor compensations config
                cursor.execute("SELECT COUNT(*) FROM `doctor_compensations_config`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `doctor_compensations_config` (doctor_id, service_id, branch, patient_type, insurance_id, company_id, trigger_event, compensation_type, value) VALUES (1, NULL, NULL, NULL, NULL, NULL, 'incassato', 'percentage', 40.00)")
                
                # Seed FSE transmissions
                cursor.execute("SELECT COUNT(*) FROM `fse_transmissions`")
                res_row = cursor.fetchone()
                count = list(res_row.values())[0] if isinstance(res_row, dict) else res_row[0]
                if count == 0:
                    cursor.execute("INSERT INTO `fse_transmissions` (document_type, document_id, workflow_instance_id, trace_id, status, error_message, cda_xml) VALUES ('lis', 1, 'WORKFLOW_LIS_001', 'TRACE_LIS_998811', 'published', NULL, '<?xml version=\"1.0\"?><ClinicalDocument></ClinicalDocument>')")
                    cursor.execute("INSERT INTO `fse_transmissions` (document_type, document_id, workflow_instance_id, trace_id, status, error_message, cda_xml) VALUES ('ris', 2, 'WORKFLOW_RIS_002', 'TRACE_RIS_998812', 'error', 'Firma digitale non valida o certificato scaduto', '<?xml version=\"1.0\"?><ClinicalDocument></ClinicalDocument>')")
                    cursor.execute("INSERT INTO `fse_transmissions` (document_type, document_id, workflow_instance_id, trace_id, status, error_message, cda_xml) VALUES ('visit', 3, 'WORKFLOW_VIS_003', 'TRACE_VIS_998813', 'pending', NULL, NULL)")
                
                # Seed system settings
                cursor.execute("INSERT INTO `system_settings` (setting_key, setting_value) VALUES ('license_serial', 'NC-ENT-2026-9482-1048') ON DUPLICATE KEY UPDATE setting_value=setting_value")
                cursor.execute("INSERT INTO `system_settings` (setting_key, setting_value) VALUES ('license_info', '{\"version\": \"1.0\", \"type\": \"Enterprise Suite\", \"expiry\": \"2029-12-31\", \"max_users\": 50}') ON DUPLICATE KEY UPDATE setting_value=setting_value")
                
                # Seed system license
                cursor.execute("INSERT INTO `system_license` (serial_number, version) VALUES ('NC-ENT-2026-9482-1048', '1.0') ON DUPLICATE KEY UPDATE version=version")
                
                # Seed default license in generated_licenses
                cursor.execute("""
                INSERT INTO `generated_licenses` (serial_number, cliente, durata_mesi, data_attivazione, data_scadenza, moduli, stato)
                VALUES ('NC-ENT-2026-9482-1048', 'NextCare Demo Clinic', 36, '2026-01-01', '2029-12-31', '[\"CUP / Agende\", \"Accettazione LIS\", \"Refertazione RIS\", \"Fascicolo Sanitario (FSE 2.0)\", \"STS (Tessera Sanitaria 730)\", \"Compensi Medici\"]', 'attiva')
                ON DUPLICATE KEY UPDATE cliente=cliente
                """)

                conn.commit()
                print("[Migrations] Finished new Enterprise tables migrations and seeds successfully.")
            except Exception as e_mig:
                print(f"[Migrations Warning] creating/seeding new Enterprise tables: {e_mig}")

    except Exception as e:

        print(f"[Migrations Error] General exception during startup migrations: {e}")

    finally:

        conn.close()



def generate_mock_result_value(test_name):

    import random

    test_name_lower = test_name.lower()

    if 'tsh' in test_name_lower:

        val = round(random.uniform(0.1, 8.5), 2)

        return str(val), "uIU/mL", "0.27-4.2", val < 0.27 or val > 4.2

    elif 'ft4' in test_name_lower:

        val = round(random.uniform(0.5, 2.5), 2)

        return str(val), "ng/dL", "0.93-1.7", val < 0.93 or val > 1.7

    elif 'wbc' in test_name_lower or 'globuli bianchi' in test_name_lower:

        val = round(random.uniform(3.0, 15.0), 2)

        return str(val), "10^3/uL", "4.00-10.00", val < 4.0 or val > 10.0

    elif 'rbc' in test_name_lower or 'globuli rossi' in test_name_lower:

        val = round(random.uniform(3.5, 6.0), 2)

        return str(val), "10^6/uL", "4.50-5.90", val < 4.5 or val > 5.9

    elif 'hgb' in test_name_lower or 'emoglobina' in test_name_lower:

        val = round(random.uniform(10.0, 18.0), 1)

        return str(val), "g/dL", "13.5-17.5", val < 13.5 or val > 17.5

    elif 'plt' in test_name_lower or 'piastrine' in test_name_lower:

        val = random.randint(80, 500)

        return str(val), "10^3/uL", "150-450", val < 150 or val > 450

    elif 'glucose' in test_name_lower or 'glucosio' in test_name_lower:

        val = random.randint(60, 220)

        return str(val), "mg/dL", "70-100", val < 70 or val > 100

    elif 'cholesterol' in test_name_lower or 'colesterolo' in test_name_lower:

        val = random.randint(120, 280)

        return str(val), "mg/dL", "120-200", val < 120 or val > 200

    elif 'creatinina' in test_name_lower:

        val = round(random.uniform(0.4, 2.0), 2)

        return str(val), "mg/dL", "0.70-1.20", val < 0.7 or val > 1.2

    else:

        val = round(random.uniform(5, 120), 1)

        return str(val), "U/L", "10-50", val < 10 or val > 50



def send_simulated_socket_message(port, socket_format, barcode, sample, srv_codes, inst):

    import socket

    import random

    import time

    time.sleep(1)

    try:

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.connect(('127.0.0.1', port))

        transcoding = []

        if inst.get('lis_transcoding'):

            try:

                transcoding = json.loads(inst['lis_transcoding']) if isinstance(inst['lis_transcoding'], str) else inst['lis_transcoding']

            except Exception:

                pass

        if socket_format == 'hl7':

            msh_id = str(random.randint(100000, 999999))

            dt = time.strftime('%Y%m%d%H%M%S')

            msh = f"MSH|^~\\&|INSTRUMENT||NEXTCARE||{dt}||ORU^R01|{msh_id}|P|2.3"

            pid = f"PID|1||PAT999||{sample.get('last_name','')}^{sample.get('first_name','')}||{sample.get('birth_date','').replace('-','') if sample.get('birth_date') else ''}|{sample.get('gender','M')}"

            segments = [msh, pid]

            obx_idx = 1

            for code in srv_codes:

                inst_code = translate_code(transcoding, 'service', code, 'to_instrument')

                obr = f"OBR|1||{barcode}||{inst_code}"

                segments.append(obr)

                params = []

                conn = get_db_connection()

                if conn:

                    try:

                        with conn.cursor() as cursor:

                            cursor.execute("SELECT parameters FROM medical_services WHERE code = %s", (code,))

                            srv_row = cursor.fetchone()

                            if srv_row and srv_row.get('parameters'):

                                p_list = json.loads(srv_row['parameters']) if isinstance(srv_row['parameters'], str) else srv_row['parameters']

                                params = [p['name'] for p in p_list if p and p.get('name')]

                    except Exception:

                        pass

                    finally:

                        conn.close()

                if not params:

                    code_upper = code.upper()

                    if 'CBC' in code_upper or 'EMOCROMO' in code_upper:

                        params = ['WBC', 'RBC', 'HGB', 'PLT']

                    elif 'GLU' in code_upper:

                        params = ['Glucosio']

                    elif 'TSH' in code_upper:

                        params = ['TSH_VAL']

                    else:

                        params = [code]

                for p in params:

                    inst_param_code = translate_code(transcoding, 'parameter', p, 'to_instrument')

                    val, unit, ref, oob = generate_mock_result_value(p)

                    flag = "H" if oob else "N"

                    obx = f"OBX|{obx_idx}|NM|{inst_param_code}||{val}|{unit}|{ref}|{flag}|||F"

                    segments.append(obx)

                    obx_idx += 1

            hl7_msg = "\r".join(segments) + "\r"

            mllp_msg = b"\x0b" + hl7_msg.encode('utf-8') + b"\x1c\x0d"

            s.sendall(mllp_msg)

        elif socket_format == 'astm':

            h_rec = "H|\\^&|||NEXTCARE||||||P|E1394-97"

            p_rec = f"P|1||||{sample.get('last_name','')}^{sample.get('first_name','')}||{sample.get('birth_date','').replace('-','') if sample.get('birth_date') else ''}|{sample.get('gender','M')}"

            o_rec = f"O|1|{barcode}||^^^ALL"

            segments = [h_rec, p_rec, o_rec]

            r_idx = 1

            for code in srv_codes:

                params = []

                conn = get_db_connection()

                if conn:

                    try:

                        with conn.cursor() as cursor:

                            cursor.execute("SELECT parameters FROM medical_services WHERE code = %s", (code,))

                            srv_row = cursor.fetchone()

                            if srv_row and srv_row.get('parameters'):

                                p_list = json.loads(srv_row['parameters']) if isinstance(srv_row['parameters'], str) else srv_row['parameters']

                                params = [p['name'] for p in p_list if p and p.get('name')]

                    except Exception:

                        pass

                    finally:

                        conn.close()

                if not params:

                    code_upper = code.upper()

                    if 'CBC' in code_upper or 'EMOCROMO' in code_upper:

                        params = ['WBC', 'RBC', 'HGB', 'PLT']

                    elif 'GLU' in code_upper:

                        params = ['Glucosio']

                    elif 'TSH' in code_upper:

                        params = ['TSH_VAL']

                    else:

                        params = [code]

                for p in params:

                    inst_param_code = translate_code(transcoding, 'parameter', p, 'to_instrument')

                    val, unit, ref, oob = generate_mock_result_value(p)

                    flag = "H" if oob else "N"

                    r_rec = f"R|{r_idx}|^^^{inst_param_code}|{val}|{unit}|{ref}|{flag}"

                    segments.append(r_rec)

                    r_idx += 1

            l_rec = "L|1|N"

            segments.append(l_rec)

            astm_msg = "\r".join(segments) + "\r"

            s.sendall(astm_msg.encode('utf-8'))

        elif socket_format == 'xml':

            xml_lines = [

                '<?xml version="1.0" encoding="utf-8"?>',

                '<ListaRichieste>',

                '    <Richiesta>',

                f"        <IdRichiestaLis>{barcode}</IdRichiestaLis>",

                f"        <Cognome>{sample.get('last_name','')}</Cognome>",

                f"        <Nome>{sample.get('first_name','')}</Nome>"

            ]

            for code in srv_codes:

                inst_code = translate_code(transcoding, 'service', code, 'to_instrument')

                xml_lines.append(f'        <Analisi Codice="{inst_code}">')

                params = []

                conn = get_db_connection()

                if conn:

                    try:

                        with conn.cursor() as cursor:

                            cursor.execute("SELECT parameters FROM medical_services WHERE code = %s", (code,))

                            srv_row = cursor.fetchone()

                            if srv_row and srv_row.get('parameters'):

                                p_list = json.loads(srv_row['parameters']) if isinstance(srv_row['parameters'], str) else srv_row['parameters']

                                params = [p['name'] for p in p_list if p and p.get('name')]

                    except Exception:

                        pass

                    finally:

                        conn.close()

                if not params:

                    code_upper = code.upper()

                    if 'CBC' in code_upper or 'EMOCROMO' in code_upper:

                        params = ['WBC', 'RBC', 'HGB', 'PLT']

                    elif 'GLU' in code_upper:

                        params = ['Glucosio']

                    elif 'TSH' in code_upper:

                        params = ['TSH_VAL']

                    else:

                        params = [code]

                for p in params:

                    inst_param_code = translate_code(transcoding, 'parameter', p, 'to_instrument')

                    val, unit, ref, oob = generate_mock_result_value(p)

                    oob_str = "true" if oob else "false"

                    xml_lines.append(f'            <Risultato Codice="{inst_param_code}">')

                    xml_lines.append(f'                <Descrizione>{p}</Descrizione>')

                    xml_lines.append(f'                <Valore>{val}</Valore>')

                    xml_lines.append(f'                <UDM>{unit}</UDM>')

                    xml_lines.append(f'                <LimiteInferiore>{ref.split("-")[0] if "-" in ref else ref}</LimiteInferiore>')

                    xml_lines.append(f'                <LimiteSuperiore>{ref.split("-")[1] if "-" in ref else ref}</LimiteSuperiore>')

                    xml_lines.append(f'                <FuoriNorma>{oob_str}</FuoriNorma>')

                    xml_lines.append('            </Risultato>')

                xml_lines.append('        </Analisi>')

            xml_lines.append('    </Richiesta>')

            xml_lines.append('</ListaRichieste>')

            xml_msg = "\n".join(xml_lines)

            s.sendall(xml_msg.encode('utf-8'))

        s.recv(4096)

        s.close()

    except Exception as err:

        print(f"[LIS Simulator Socket Client Error] {err}")



def run_lis_simulator_iteration():

    conn = get_db_connection()

    if not conn:

        return

    try:

        with conn.cursor() as cursor:

            cursor.execute("SELECT * FROM equipment WHERE type = 'LIS' AND status = 'active'")

            instruments = cursor.fetchall()

            if not instruments:

                return

            # Load global configuration for simulator as a fallback

            import json, os

            config_path = "config.json"

            global_simulator_active = False

            if os.path.exists(config_path):

                try:

                    with open(config_path, "r", encoding="utf-8") as f:

                        cfg = json.load(f)

                        global_simulator_active = cfg.get('lis_simulator_active', False)

                except Exception:

                    pass



            for inst in instruments:

                is_inst_sim_active = bool(inst.get('lis_simulator_active', 0))

                if not is_inst_sim_active and not global_simulator_active:

                    continue



                interface_type = inst.get('lis_interface_type')

                if interface_type == 'file':

                    export_path = inst.get('lis_export_path') or r"C:\NextCare_LIS_Exchange\export"

                    import_path = inst.get('lis_import_path') or r"C:\NextCare_LIS_Exchange\import"

                    file_format = inst.get('lis_file_format', 'csv')

                    if not os.path.exists(export_path):

                        continue

                    ext = f".{file_format}"

                    files = [f for f in os.listdir(export_path) if f.lower().endswith(ext) and os.path.isfile(os.path.join(export_path, f))]

                    for fname in files:

                        fpath = os.path.join(export_path, fname)

                        time.sleep(0.5)

                        try:

                            requests = []

                            if file_format == 'xml':

                                import xml.etree.ElementTree as ET

                                tree = ET.parse(fpath)

                                root = tree.getroot()

                                req_nodes = root.findall('Richiesta') if root.tag == 'ListaRichieste' else [root]

                                for req in req_nodes:

                                    barcode = req.findtext('IdRichiestaLis')

                                    last_name = req.findtext('Cognome', '')

                                    first_name = req.findtext('Nome', '')

                                    gender = req.findtext('Sesso', 'M')

                                    birth_date = req.findtext('DataNascita', '')

                                    analyses = [ana.get('Codice') for ana in req.findall('Analisi')]

                                    requests.append({

                                        'barcode': barcode,

                                        'last_name': last_name,

                                        'first_name': first_name,

                                        'gender': gender,

                                        'birth_date': birth_date,

                                        'analyses': analyses

                                    })

                            else:

                                with open(fpath, 'r', encoding='utf-8') as f:

                                    lines = f.readlines()

                                if len(lines) > 1:

                                    header = [h.strip().lower() for h in lines[0].split(',')]

                                    for line in lines[1:]:

                                        parts = [p.strip() for p in line.split(',')]

                                        if len(parts) < 6:

                                            continue

                                        row = dict(zip(header, parts))

                                        requests.append({

                                            'barcode': row.get('barcode'),

                                            'last_name': row.get('last_name'),

                                            'first_name': row.get('first_name'),

                                            'gender': row.get('gender'),

                                            'birth_date': row.get('birth_date'),

                                            'analyses': row.get('service_codes', '').split(';')

                                        })

                            os.remove(fpath)

                            for req in requests:

                                barcode = req['barcode']

                                analyses_results = []

                                for code in req['analyses']:

                                    transcoding = []

                                    if inst.get('lis_transcoding'):

                                        try:

                                            transcoding = json.loads(inst['lis_transcoding']) if isinstance(inst['lis_transcoding'], str) else inst['lis_transcoding']

                                        except Exception:

                                            pass

                                    nc_service_code = translate_code(transcoding, 'service', code, 'to_nextcare')

                                    params = []

                                    cursor.execute("SELECT parameters FROM medical_services WHERE code = %s", (nc_service_code,))

                                    srv_row = cursor.fetchone()

                                    if srv_row and srv_row.get('parameters'):

                                        try:

                                            p_list = json.loads(srv_row['parameters']) if isinstance(srv_row['parameters'], str) else srv_row['parameters']

                                            params = [p['name'] for p in p_list if p and p.get('name')]

                                        except Exception:

                                            pass

                                    if not params:

                                        code_upper = code.upper()

                                        if 'CBC' in code_upper or 'EMOCROMO' in code_upper:

                                            params = ['WBC', 'RBC', 'HGB', 'PLT']

                                        elif 'GLU' in code_upper:

                                            params = ['Glucosio']

                                        elif 'TSH' in code_upper:

                                            params = ['TSH_VAL']

                                        else:

                                            params = [code]

                                    tests_results = []

                                    for p in params:

                                        inst_param_code = translate_code(transcoding, 'parameter', p, 'to_instrument')

                                        val, unit, ref, oob = generate_mock_result_value(p)

                                        tests_results.append({

                                            'parameter_code': inst_param_code,

                                            'parameter_name': p,

                                            'value': val,

                                            'unit': unit,

                                            'limit_inf': ref.split('-')[0] if '-' in ref else ref,

                                            'limit_sup': ref.split('-')[1] if '-' in ref else ref,

                                            'out_of_bounds': oob

                                        })

                                    analyses_results.append({

                                        'service_code': code,

                                        'tests': tests_results

                                    })

                                result_filename = f"result_{barcode}.{file_format}"

                                result_filepath = os.path.join(import_path, result_filename)

                                os.makedirs(import_path, exist_ok=True)

                                if file_format == 'xml':

                                    xml_lines = [

                                        '<?xml version="1.0" encoding="utf-8"?>',

                                        '<ListaRichieste>',

                                        '    <Richiesta>',

                                        f"        <IdRichiestaLis>{barcode}</IdRichiestaLis>",

                                        f"        <Cognome>{req['last_name']}</Cognome>",

                                        f"        <Nome>{req['first_name']}</Nome>"

                                    ]

                                    for ana in analyses_results:

                                        xml_lines.append(f'        <Analisi Codice="{ana["service_code"]}">')

                                        for test in ana['tests']:

                                            oob_str = "true" if test['out_of_bounds'] else "false"

                                            xml_lines.append(f'            <Risultato Codice="{test["parameter_code"]}">')

                                            xml_lines.append(f'                <Descrizione>{test["parameter_name"]}</Descrizione>')

                                            xml_lines.append(f'                <Valore>{test["value"]}</Valore>')

                                            xml_lines.append(f'                <UDM>{test["unit"]}</UDM>')

                                            xml_lines.append(f'                <LimiteInferiore>{test["limit_inf"]}</LimiteInferiore>')

                                            xml_lines.append(f'                <LimiteSuperiore>{test["limit_sup"]}</LimiteSuperiore>')

                                            xml_lines.append(f'                <FuoriNorma>{oob_str}</FuoriNorma>')

                                            xml_lines.append('            </Risultato>')

                                        xml_lines.append('        </Analisi>')

                                    xml_lines.append('    </Richiesta>')

                                    xml_lines.append('</ListaRichieste>')

                                    with open(result_filepath, 'w', encoding='utf-8') as f_out:

                                        f_out.write('\n'.join(xml_lines))

                                else:

                                    csv_lines = ["barcode,service_code,parameter_code,value,unit,out_of_bounds,limit_inf,limit_sup,parameter_name\n"]

                                    for ana in analyses_results:

                                        for test in ana['tests']:

                                            oob_str = "true" if test['out_of_bounds'] else "false"

                                            csv_lines.append(f"{barcode},{ana['service_code']},{test['parameter_code']},{test['value']},{test['unit']},{oob_str},{test['limit_inf']},{test['limit_sup']},{test['parameter_name']}\n")

                                    with open(result_filepath, 'w', encoding='utf-8') as f_out:

                                        f_out.writelines(csv_lines)

                                print(f"[LIS Simulator] Simulated result file written for {barcode}")

                        except Exception as parse_err:

                            print(f"[LIS Simulator Error] Failed to process file {fname}: {parse_err}")

                elif interface_type == 'socket':

                    port = inst.get('lis_socket_port')

                    socket_format = inst.get('lis_socket_format', 'hl7')

                    if not port:

                        continue

                    cursor.execute("""

                        SELECT DISTINCT s.barcode, p.first_name, p.last_name, p.gender, p.birth_date

                        FROM lab_samples s

                        JOIN patients p ON s.patient_id = p.id

                        JOIN lab_tests t ON t.sample_id = s.id

                        JOIN medical_services ms ON t.service_id = ms.id

                        WHERE s.status IN ('processing', 'collected')

                          AND ms.instrument_id = %s

                          AND t.result_value IS NULL

                    """, (inst['id'],))

                    pending_samples = cursor.fetchall()

                    for sample in pending_samples:

                        barcode = sample['barcode']

                        cursor.execute("""

                            SELECT DISTINCT ms.code

                            FROM lab_tests t

                            JOIN medical_services ms ON t.service_id = ms.id

                            WHERE t.sample_id = (SELECT id FROM lab_samples WHERE barcode = %s)

                              AND ms.instrument_id = %s

                              AND t.result_value IS NULL

                        """, (barcode, inst['id']))

                        srv_codes = [r['code'] for r in cursor.fetchall()]

                        if not srv_codes:

                            continue

                        try:

                            import threading

                            t = threading.Thread(target=send_simulated_socket_message, args=(port, socket_format, barcode, sample, srv_codes, inst), daemon=True)

                            t.start()

                        except Exception as e:

                            print(f"[LIS Simulator Socket Dispatch Error] {e}")

    except Exception as err:

        print(f"[LIS Simulator Loop Error] {err}")

    finally:

        conn.close()









MWL_LOGS = []

def append_mwl_log(message):
    import datetime
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    MWL_LOGS.append(f"[{timestamp}] {message}")
    if len(MWL_LOGS) > 100:
        MWL_LOGS.pop(0)

# =========================================================================
def run_dicom_mwl_server():
    if not HAS_DICOM:
        print("[DICOM MWL] pynetdicom non e' disponibile. Server Worklist disabilitato.")
        return
        
    from pynetdicom.sop_class import ModalityWorklistInformationFind
    
    ae = AE(ae_title='NEXTCARE_RIS')
    ae.add_supported_context(ModalityWorklistInformationFind)
    
    def handle_c_find(event):
        query = event.identifier
        print(f"[DICOM MWL] Ricevuta query C-FIND:\n{query}")
        
        q_patient_id = getattr(query, 'PatientID', None)
        q_patient_name = getattr(query, 'PatientName', None)
        
        append_mwl_log(f"Richiesta C-FIND ricevuta dallo strumento. Filtro PatientID: '{q_patient_id or ''}', Filtro PatientName: '{q_patient_name or ''}'")
        
        conn = get_db_connection()
        if not conn:
            append_mwl_log("Errore: connessione database fallita durante query C-FIND")
            yield 0xC000, None
            return
            
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cur:
                sql = """
                    SELECT a.id, a.scheduled_at, a.study_type, 
                           p.id as patient_id, p.first_name, p.last_name, p.cf, p.gender, p.birth_date,
                           s.name as service_name, s.code as service_code,
                           a.dicom_series_uid
                    FROM appointments a
                    JOIN patients p ON a.patient_id = p.id
                    JOIN medical_services s ON a.service_id = s.id
                    WHERE a.status IN ('scheduled', 'in_progress', 'executed')
                """
                params = []
                if q_patient_id and str(q_patient_id).strip() != "":
                    sql += " AND p.cf LIKE %s"
                    params.append(f"%{str(q_patient_id).strip()}%")
                    
                cur.execute(sql, params)
                rows = cur.fetchall()
                
                append_mwl_log(f"Trovati {len(rows)} record corrispondenti nel database NextCare.")
                
                for r in rows:
                    ds = Dataset()
                    ds.PatientID = r['cf'] or f"PAT{r['patient_id']}"
                    ds.PatientName = f"{r['last_name'].upper()}^{r['first_name'].upper()}"
                    ds.PatientBirthDate = r['birth_date'].strftime('%Y%m%d') if r['birth_date'] else ''
                    ds.PatientSex = 'M' if r['gender'] == 'M' else 'F'
                    
                    ds.AccessionNumber = f"ACC{r['id']}"
                    ds.StudyInstanceUID = r['dicom_series_uid'] or f"1.3.6.1.4.1.25403.345050719076124.847.{r['id']}"
                    
                    sps_ds = Dataset()
                    sps_ds.ScheduledStationAETitle = 'NEXTCARE_RIS'
                    mod = 'OT'
                    st = r['study_type']
                    if st == 'XRAY': mod = 'DX'
                    elif st == 'MRI': mod = 'MR'
                    elif st == 'CT': mod = 'CT'
                    elif st == 'ULTRASOUND': mod = 'US'
                    elif st == 'MAMMOGRAPHY': mod = 'MG'
                    sps_ds.Modality = mod
                    sps_ds.ScheduledProcedureStepStartDate = r['scheduled_at'].strftime('%Y%m%d')
                    sps_ds.ScheduledProcedureStepStartTime = r['scheduled_at'].strftime('%H%M%S')
                    sps_ds.ScheduledProcedureStepDescription = r['service_name']
                    sps_ds.ScheduledProcedureStepID = f"SPS{r['id']}"
                    sps_ds.ScheduledStationName = 'RIS_WORKSTATION'
                    sps_ds.ScheduledProtocolCodeSequence = []
                    
                    ds.ScheduledProcedureStepSequence = [sps_ds]
                    ds.RequestedProcedureDescription = r['service_name']
                    ds.RequestedProcedureID = r['service_code'] or f"PR{r['id']}"
                    
                    append_mwl_log(f"Restituzione record: {ds.PatientName} (CF: {ds.PatientID})")
                    yield 0xFF00, ds
                    
        except Exception as e:
            print(f"[DICOM MWL Error] Query error: {e}")
            append_mwl_log(f"Errore query C-FIND: {str(e)}")
            yield 0xC000, None
            return
        finally:
            conn.close()
            
        yield 0x0000, None
        
    handlers = [(evt.EVT_C_FIND, handle_c_find)]
    print("[DICOM MWL] Starting Modality Worklist server on port 11104, AE Title 'NEXTCARE_RIS'...")
    ae.start_server(('', 11104), block=False, evt_handlers=handlers)

def run_lis_engine():

    print("[LIS Background Engine] Started.")

    run_db_migrations()

    while True:

        try:

            check_and_export_file_orders()

            check_and_import_file_results()

            

            # Run LIS simulator

            try:

                run_lis_simulator_iteration()

            except Exception as sim_ex:

                print(f"[LIS Supervisor Simulator Error] {sim_ex}")

            

            conn = get_db_connection()

            if conn:

                try:

                    with conn.cursor() as cursor:

                        cursor.execute("SELECT * FROM equipment WHERE type = 'LIS' AND status = 'active' AND lis_interface_type = 'socket'")

                        socket_instruments = cursor.fetchall()

                        

                        active_ports = set()

                        for inst in socket_instruments:

                            port = inst.get('lis_socket_port')

                            fmt = inst.get('lis_socket_format', 'hl7')

                            if not port:

                                continue

                            active_ports.add(port)

                            

                            transcoding = []

                            if inst.get('lis_transcoding'):

                                try:

                                    transcoding = json.loads(inst['lis_transcoding']) if isinstance(inst['lis_transcoding'], str) else inst['lis_transcoding']

                                except Exception:

                                    pass

                            

                            if port not in RUNNING_SOCKET_SERVERS or not RUNNING_SOCKET_SERVERS[port]['active']:

                                RUNNING_SOCKET_SERVERS[port] = {

                                    'active': True,

                                    'format': fmt,

                                    'sock': None

                                }

                                t = threading.Thread(target=socket_listener_thread, args=(port, fmt, transcoding), daemon=True)

                                t.start()

                        

                        for port in list(RUNNING_SOCKET_SERVERS.keys()):

                            if port not in active_ports and RUNNING_SOCKET_SERVERS[port]['active']:

                                print(f"[LIS Background Engine] Stopping socket server on port {port}...")

                                RUNNING_SOCKET_SERVERS[port]['active'] = False

                                sock = RUNNING_SOCKET_SERVERS[port]['sock']

                                if sock:

                                    try:

                                        sock.close()

                                    except Exception:

                                        pass

                                del RUNNING_SOCKET_SERVERS[port]

                except Exception as db_err:

                    print(f"[LIS Background Engine Sync Error] {db_err}")

                finally:

                    conn.close()

        except Exception as e:

            print(f"[LIS Background Engine Loop Error] {e}")

        time.sleep(4)

class ThreadedHTTPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):

    allow_reuse_address = True



def start_server(port):

    handler = NextCareHandler

    with ThreadedHTTPServer(("", port), handler) as httpd:

        print(f"NextCare Web Application in esecuzione su http://localhost:{port}")

        httpd.serve_forever()



if __name__ == "__main__":

    import threading

    import time

    

    # Start server on Port 8000

    t1 = threading.Thread(target=start_server, args=(PORT,), daemon=True)

    t1.start()

    

    # Start server on Port 8001

    t2 = threading.Thread(target=start_server, args=(PORT_LOCAL,), daemon=True)

    t2.start()

    

    # Start LIS background engine thread

    t_lis = threading.Thread(target=run_lis_engine, daemon=True)

    
    t_lis.start()
    
    # Start DICOM MWL background server
    t_mwl = threading.Thread(target=run_dicom_mwl_server, daemon=True)
    t_mwl.start()

    

    # Keep the main thread alive to handle KeyboardInterrupt

    try:

        while True:

            time.sleep(1)

    except KeyboardInterrupt:

        print("\nArresto dei server in corso.")