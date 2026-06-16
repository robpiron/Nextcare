import sys
import os

try:
    import mysql.connector
    HAS_CONNECTOR = True
except ImportError:
    try:
        import pymysql
        HAS_CONNECTOR = False
    except ImportError:
        print("Errore: Per eseguire questo script e verificare la connessione reale a MySQL, installare prima il driver.")
        print("Esegui: pip install mysql-connector-python  oppure  pip install PyMySQL")
        sys.exit(1)

def run_test():
    print("====================================================================")
    print("       NextCare - Verifica di Funzionamento Connessione MySQL       ")
    print("====================================================================")
    
    # Defaults
    host = input("Inserisci Host MySQL [default: localhost]: ").strip() or "localhost"
    port = input("Inserisci Porta MySQL [default: 3306]: ").strip() or "3306"
    user = input("Inserisci Username [default: root]: ").strip() or "root"
    password = input("Inserisci Password: ").strip()
    db_name = input("Inserisci Nome Database [default: nextcare_db]: ").strip() or "nextcare_db"
    
    try:
        port_num = int(port)
    except ValueError:
        print("Errore: La porta deve essere un numero.")
        sys.exit(1)
        
    print("\nTentativo di connessione in corso...")
    
    try:
        if HAS_CONNECTOR:
            conn = mysql.connector.connect(
                host=host,
                port=port_num,
                user=user,
                password=password,
                connect_timeout=5
            )
        else:
            conn = pymysql.connect(
                host=host,
                port=port_num,
                user=user,
                password=password,
                timeout=5
            )
            
        print("[OK] Connessione di base al server MySQL stabilita con successo!")
        cursor = conn.cursor()
        
        # Create database if not exists
        print(f"Verifica/Creazione database '{db_name}'...")
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.execute(f"USE {db_name}")
        print(f"[OK] Database '{db_name}' pronto all'uso.")
        
        # Read schema.sql
        schema_path = "schema.sql"
        if not os.path.exists(schema_path):
            # Try to look in NextCareApp
            schema_path = os.path.join("..", "schema.sql")
            
        if os.path.exists(schema_path):
            print(f"Esecuzione schema DDL da '{schema_path}'...")
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
            queries = reconstructed_sql.split(";")
            success_queries = 0
            for query in queries:
                q = query.strip()
                if q:
                    if q.upper().startswith("CREATE DATABASE") or q.upper().startswith("USE"):
                        continue
                    try:
                        cursor.execute(q)
                        success_queries += 1
                    except Exception as err:
                        # Skip errors like database already exists warnings, or print actual errors
                        if "already exists" not in str(err).lower():
                            print(f"[WARNING] Errore in query: {err}")
            
            print(f"[OK] Eseguite {success_queries} istruzioni SQL dello schema.")
            
        else:
            print("[WARNING] File schema.sql non trovato per l'inizializzazione delle tabelle.")
            
        # Verify tables
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]
        print("\nTabelle presenti nel database:")
        for t in tables:
            print(f"  - {t}")
            
        required_tables = ['patients', 'staff', 'doctors', 'doctor_agendas', 'doctor_agenda_services', 'medical_services', 'appointments', 'appointment_services', 'lab_samples', 'lab_tests', 'radiology_studies', 'admissions', 'invoices', 'shifts']
        missing = [rt for rt in required_tables if rt not in tables]
        
        if not missing:
            print("\n[SUCCESS] Tutte le tabelle di NextCare sono state verificate con successo!")
            print("Il database relazionale MySQL è pienamente operativo e conforme.")
        else:
            print(f"\n[WARNING] Tabelle mancanti nel database: {', '.join(missing)}")
            
        conn.close()
        
    except Exception as err:
        print(f"\n[ERROR] Impossibile connettersi al server MySQL.")
        print(f"Dettaglio errore: {err}")
        print("\nSuggerimenti:")
        print("1. Verifica che il servizio MySQL sia attivo sul server di destinazione.")
        print("2. Controlla host, porta, username e password inseriti.")
        print("3. Assicurati che l'utente disponga dei privilegi necessari per creare il database.")

if __name__ == "__main__":
    run_test()
