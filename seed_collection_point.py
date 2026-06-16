import pymysql
import json
import os

def seed_collection_point():
    # Load db config
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    with open(config_path, "r", encoding="utf-8") as f:
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
    cursor = conn.cursor()

    try:
        # Check if PP-OSTIA exists
        cursor.execute("SELECT id FROM `lis_collection_points` WHERE `code` = 'PP-OSTIA'")
        cp = cursor.fetchone()
        
        if not cp:
            cursor.execute("""
            INSERT INTO `lis_collection_points` 
            (`code`, `name`, `address`, `phone`, `email`, `username`, `password`, `invoice_separate`, `invoice_prefix`, `invoice_next_num`)
            VALUES
            ('PP-OSTIA', 'Ostia', 'Via del Mare, 12', '061234567', 'ostia@nextcare.it', 'ostia', 'ostia123', 1, 'FAT-OST-', 1)
            """)
            conn.commit()
            cursor.execute("SELECT id FROM `lis_collection_points` WHERE `code` = 'PP-OSTIA'")
            cp = cursor.fetchone()
            print("Collection point 'Ostia' (PP-OSTIA) inserted.")
        else:
            print("Collection point 'Ostia' (PP-OSTIA) already exists.")

        cp_id = cp['id']

        # Ensure some patients exist
        cursor.execute("SELECT id FROM `patients` LIMIT 3")
        patients = cursor.fetchall()
        if not patients:
            # Insert a test patient
            cursor.execute("""
            INSERT INTO `patients` 
            (`first_name`, `last_name`, `cf`, `tax_code`, `gender`, `birth_date`, `phone`, `email`, `address`)
            VALUES
            ('Mario', 'Rossi', 'RSSMRA80A01H501U', 'RSSMRA80A01H501U', 'M', '1980-01-01', '3331234567', 'mario.rossi@gmail.com', 'Via Roma 1')
            """)
            conn.commit()
            cursor.execute("SELECT id FROM `patients` LIMIT 3")
            patients = cursor.fetchall()
            print("Test patient inserted.")

        patient_id = patients[0]['id']

        # Check if we have sample for Ostia
        cursor.execute("SELECT id FROM `lab_samples` WHERE `collection_point_id` = %s", (cp_id,))
        sample = cursor.fetchone()
        
        if not sample:
            # Let's insert a couple of samples for PP-OSTIA
            cursor.execute("""
            INSERT INTO `lab_samples` 
            (`barcode`, `patient_id`, `sample_type`, `status`, `collection_point_id`, `created_at`, `collected_at`)
            VALUES
            ('OST-00001', %s, 'sangue', 'collected', %s, NOW(), NOW()),
            ('OST-00002', %s, 'urine', 'collected', %s, NOW(), NULL)
            """, (patient_id, cp_id, patient_id, cp_id))
            
            # Let's insert tests for these samples
            conn.commit()
            cursor.execute("SELECT id, barcode FROM `lab_samples` WHERE `collection_point_id` = %s", (cp_id,))
            samples = cursor.fetchall()
            
            for s in samples:
                if s['barcode'] == 'OST-00001':
                    cursor.execute("""
                    INSERT INTO `lab_tests`
                    (`sample_id`, `test_name`, `service_id`, `status`, `result_value`, `unit`, `reference_range`)
                    VALUES
                    (%s, 'Emocromo', 1, 'flagged', '12.5', 'g/dL', '13.5 - 17.5'),
                    (%s, 'Glicemia', 2, 'completed', '95', 'mg/dL', '70 - 110')
                    """, (s['id'], s['id']))
                else:
                    cursor.execute("""
                    INSERT INTO `lab_tests`
                    (`sample_id`, `test_name`, `service_id`, `status`, `result_value`, `unit`, `reference_range`)
                    VALUES
                    (%s, 'Urinocoltura', 3, 'pending', NULL, NULL, 'Negativo')
                    """, (s['id']))
            conn.commit()
            print("Test samples for PP-OSTIA inserted.")
        else:
            print("Test samples for PP-OSTIA already exist.")

        # Let's trigger a db-sync of these tables so the frontend gets them
        print("Done seeding collection point data.")
    except Exception as e:
        conn.rollback()
        print("Error during seed:", e)
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    seed_collection_point()
