import pymysql
import json
import os
import datetime

def seed_ddt_examples():
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
        # Get collection point ID
        cursor.execute("SELECT id FROM `lis_collection_points` WHERE `code` = 'PP-OSTIA'")
        cp = cursor.fetchone()
        if not cp:
            # Insert collection point Ostia
            cursor.execute("""
            INSERT INTO `lis_collection_points` 
            (`code`, `name`, `address`, `phone`, `email`, `username`, `password`, `invoice_separate`, `invoice_prefix`, `invoice_next_num`)
            VALUES
            ('PP-OSTIA', 'Ostia', 'Via del Mare, 12', '061234567', 'ostia@nextcare.it', 'ostia', 'ostia123', 1, 'FAT-OST-', 1)
            """)
            conn.commit()
            cursor.execute("SELECT id FROM `lis_collection_points` WHERE `code` = 'PP-OSTIA'")
            cp = cursor.fetchone()
            print("Collection point 'Ostia' (PP-OSTIA) created.")
        
        cp_id = cp['id']

        # Get or create patient
        cursor.execute("SELECT id FROM `patients` LIMIT 1")
        patient = cursor.fetchone()
        if not patient:
            import uuid
            patient_uuid = str(uuid.uuid4())
            cursor.execute("""
            INSERT INTO `patients` 
            (`first_name`, `last_name`, `cf`, `tax_code`, `gender`, `birth_date`, `phone`, `email`, `address`, `uuid`)
            VALUES
            ('Mario', 'Rossi', 'RSSMRA80A01H501U', 'RSSMRA80A01H501U', 'M', '1980-01-01', '3331234567', 'mario.rossi@gmail.com', 'Via Roma 1', %s)
            """, (patient_uuid,))
            conn.commit()
            cursor.execute("SELECT id FROM `patients` LIMIT 1")
            patient = cursor.fetchone()
            print("Patient created.")
        
        patient_id = patient['id']

        # Clean existing test samples/ddts to keep seeding clean and idempotent
        cursor.execute("SELECT id FROM `lis_ddt` WHERE `ddt_code` IN ('DDT-PP-OSTIA-20260614-10001', 'DDT-PP-OSTIA-20260614-20002')")
        existing_ddts = cursor.fetchall()
        if existing_ddts:
            ddt_ids = [str(d['id']) for d in existing_ddts]
            cursor.execute(f"DELETE FROM `lab_tests` WHERE `sample_id` IN (SELECT id FROM `lab_samples` WHERE `ddt_id` IN ({','.join(ddt_ids)}))")
            cursor.execute(f"DELETE FROM `lab_samples` WHERE `ddt_id` IN ({','.join(ddt_ids)})")
            cursor.execute(f"DELETE FROM `lis_ddt` WHERE `id` IN ({','.join(ddt_ids)})")
            conn.commit()
            print("Cleaned up old test DDTs, samples and tests.")

        # Let's insert DDT 1 ("in viaggio")
        # samples_json stores stringified JSON array
        samples_json1 = json.dumps(["100090010001", "100090020005"])
        cursor.execute("""
        INSERT INTO `lis_ddt` 
        (`ddt_code`, `collection_point_id`, `status`, `shipped_at`, `received_at`, `received_by`, `samples_json`)
        VALUES
        ('DDT-PP-OSTIA-20260614-10001', %s, 'in viaggio', NOW(), NULL, NULL, %s)
        """, (cp_id, samples_json1))
        conn.commit()
        
        cursor.execute("SELECT id FROM `lis_ddt` WHERE `ddt_code` = 'DDT-PP-OSTIA-20260614-10001'")
        ddt1 = cursor.fetchone()
        ddt1_id = ddt1['id']

        # Let's insert DDT 2 ("arrivato in lab")
        samples_json2 = json.dumps(["100090030001", "100090040005"])
        # received_at 4 hours ago, shipped 5 hours ago
        shipped_time = datetime.datetime.now() - datetime.timedelta(hours=5)
        received_time = datetime.datetime.now() - datetime.timedelta(hours=4)
        cursor.execute("""
        INSERT INTO `lis_ddt` 
        (`ddt_code`, `collection_point_id`, `status`, `shipped_at`, `received_at`, `received_by`, `samples_json`)
        VALUES
        ('DDT-PP-OSTIA-20260614-20002', %s, 'arrivato in lab', %s, %s, 1, %s)
        """, (cp_id, shipped_time, received_time, samples_json2))
        conn.commit()

        cursor.execute("SELECT id FROM `lis_ddt` WHERE `ddt_code` = 'DDT-PP-OSTIA-20260614-20002'")
        ddt2 = cursor.fetchone()
        ddt2_id = ddt2['id']

        # Insert samples for DDT 1 (status = 'collected' or 'received' depending on LIS status)
        # Note: Samples for a shipped DDT have status 'collected' (prelevati al punto prelievo)
        cursor.execute("""
        INSERT INTO `lab_samples` 
        (`barcode`, `patient_id`, `sample_type`, `status`, `collection_point_id`, `ddt_id`, `created_at`, `collected_at`)
        VALUES
        ('100090010001', %s, 'sangue', 'collected', %s, %s, NOW(), NOW()),
        ('100090020005', %s, 'urine', 'collected', %s, %s, NOW(), NOW())
        """, (patient_id, cp_id, ddt1_id, patient_id, cp_id, ddt1_id))
        conn.commit()

        # Insert samples for DDT 2 (status = 'collected' or 'received' since DDT arrived)
        cursor.execute("""
        INSERT INTO `lab_samples` 
        (`barcode`, `patient_id`, `sample_type`, `status`, `collection_point_id`, `ddt_id`, `created_at`, `collected_at`)
        VALUES
        ('100090030001', %s, 'sangue', 'collected', %s, %s, NOW(), NOW()),
        ('100090040005', %s, 'urine', 'collected', %s, %s, NOW(), NOW())
        """, (patient_id, cp_id, ddt2_id, patient_id, cp_id, ddt2_id))
        conn.commit()

        # Get sample IDs
        cursor.execute("SELECT id, barcode FROM `lab_samples` WHERE `barcode` IN ('100090010001', '100090020005', '100090030001', '100090040005')")
        samples = cursor.fetchall()
        sample_ids = {s['barcode']: s['id'] for s in samples}

        # Insert tests for DDT 1
        cursor.execute("""
        INSERT INTO `lab_tests`
        (`sample_id`, `test_name`, `service_id`, `status`, `result_value`, `unit`, `reference_range`)
        VALUES
        (%s, 'Glicemia', 2, 'pending', NULL, 'mg/dL', '70 - 110')
        """, (sample_ids['100090010001']))

        cursor.execute("""
        INSERT INTO `lab_tests`
        (`sample_id`, `test_name`, `service_id`, `status`, `result_value`, `unit`, `reference_range`)
        VALUES
        (%s, 'Urinocoltura', 3, 'pending', NULL, NULL, 'Negativo')
        """, (sample_ids['100090020005']))

        # Insert tests for DDT 2
        cursor.execute("""
        INSERT INTO `lab_tests`
        (`sample_id`, `test_name`, `service_id`, `status`, `result_value`, `unit`, `reference_range`)
        VALUES
        (%s, 'Creatinina', 4, 'completed', '0.9', 'mg/dL', '0.7 - 1.2')
        """, (sample_ids['100090030001']))

        cursor.execute("""
        INSERT INTO `lab_tests`
        (`sample_id`, `test_name`, `service_id`, `status`, `result_value`, `unit`, `reference_range`)
        VALUES
        (%s, 'Esame delle Urine', 5, 'completed', 'Ph 6.0', '', '5.5 - 7.5')
        """, (sample_ids['100090040005']))

        conn.commit()
        print("DDT examples seeded successfully.")

    except Exception as e:
        conn.rollback()
        print("Error during seed:", e)
        raise e
    finally:
        conn.close()

if __name__ == "__main__":
    seed_ddt_examples()
