from server import get_db_connection

conn = get_db_connection()
if conn:
    try:
        with conn.cursor() as cur:
            cur.execute("ALTER TABLE `lab_samples` MODIFY COLUMN `status` ENUM('da prelevare', 'collected', 'received', 'processing', 'to_validate', 'completed', 'rejected', 'suspended') NOT NULL DEFAULT 'da prelevare'")
            conn.commit()
            print("Successfully updated status enum column in lab_samples table!")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()
