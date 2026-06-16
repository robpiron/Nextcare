from server import get_db_connection

conn = get_db_connection()
if conn:
    try:
        with conn.cursor() as cur:
            # Check if column already exists
            cur.execute("SHOW COLUMNS FROM `lab_samples` LIKE 'bulk_session_uid'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE `lab_samples` ADD COLUMN `bulk_session_uid` VARCHAR(50) NULL")
                conn.commit()
                print("Successfully added bulk_session_uid column to lab_samples!")
            else:
                print("Column bulk_session_uid already exists.")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()
