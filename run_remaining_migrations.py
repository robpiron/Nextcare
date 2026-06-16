from server import get_db_connection

conn = get_db_connection()
if conn:
    try:
        with conn.cursor() as cur:
            # 1. Create companies table
            cur.execute("""
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
            print("Verified / Created companies table.")

            # 2. Create ris_report_templates table
            cur.execute("""
            CREATE TABLE IF NOT EXISTS `ris_report_templates` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `title` VARCHAR(255) NOT NULL,
                `content` TEXT NOT NULL,
                `service_id` INT NULL,
                `doctor_ids` VARCHAR(255) NULL,
                `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            print("Verified / Created ris_report_templates table.")

            # 3. Add company_id and is_company_post to invoices
            cur.execute("SHOW COLUMNS FROM `invoices` LIKE 'company_id'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE `invoices` ADD COLUMN `company_id` INT NULL")
                cur.execute("ALTER TABLE `invoices` ADD FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL")
                print("Added company_id to invoices.")
            else:
                print("company_id already exists in invoices.")

            cur.execute("SHOW COLUMNS FROM `invoices` LIKE 'is_company_post'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE `invoices` ADD COLUMN `is_company_post` TINYINT(1) NOT NULL DEFAULT 0")
                print("Added is_company_post to invoices.")
            else:
                print("is_company_post already exists in invoices.")

            # 4. Add company_id to admissions
            cur.execute("SHOW COLUMNS FROM `admissions` LIKE 'company_id'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE `admissions` ADD COLUMN `company_id` INT NULL")
                cur.execute("ALTER TABLE `admissions` ADD FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL")
                print("Added company_id to admissions.")
            else:
                print("company_id already exists in admissions.")

            # 5. Seed default companies if empty
            cur.execute("SELECT COUNT(*) FROM `companies`")
            row = cur.fetchone()
            count = list(row.values())[0] if row else 0
            if count == 0:
                cur.execute("""
                INSERT INTO `companies` (name, vat_number, fiscal_code, address, email, phone, price_list_id, billing_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, ("Acme Corporation S.r.l.", "IT01234567890", "01234567890", "Via delle Industrie 10, Milano", "amministrazione@acme.it", "02-123456", 2, "company_post"))
                
                cur.execute("""
                INSERT INTO `companies` (name, vat_number, fiscal_code, address, email, phone, price_list_id, billing_type) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, ("BioTech Health Group", "IT09876543210", "09876543210", "Corso Roma 45, Torino", "info@biotechhealth.it", "011-987654", 1, "patient"))
                print("Seeded default companies in database.")

            # 6. Run auto_detect_updates for dynamic news
            try:
                from server import auto_detect_updates
                auto_detect_updates(conn)
                print("Executed auto_detect_updates during migration.")
            except Exception as ade:
                print(f"Failed to run auto_detect_updates during migration: {ade}")

            conn.commit()
            print("Migration completed successfully!")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()
