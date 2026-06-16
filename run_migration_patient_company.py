from server import get_db_connection

conn = get_db_connection()
if conn:
    try:
        with conn.cursor() as cur:
            # Check if column already exists
            cur.execute("SHOW COLUMNS FROM `patients` LIKE 'company_id'")
            if not cur.fetchone():
                cur.execute("ALTER TABLE `patients` ADD COLUMN `company_id` INT NULL")
                cur.execute("ALTER TABLE `patients` ADD FOREIGN KEY (`company_id`) REFERENCES `companies`(`id`) ON DELETE SET NULL")
                conn.commit()
                print("Successfully added company_id column to patients!")
            else:
                print("Column company_id already exists in patients.")
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()
