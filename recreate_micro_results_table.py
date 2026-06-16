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

queries = [
    "DROP TABLE IF EXISTS `lis_microbiology_results`;",
    """
    CREATE TABLE `lis_microbiology_results` (
      `id` INT AUTO_INCREMENT PRIMARY KEY,
      `test_id` INT NOT NULL,
      `is_negative` TINYINT(1) NOT NULL DEFAULT 1,
      `notes` TEXT NULL,
      `germ1_id` INT NULL,
      `germ1_antibiotics` TEXT NULL,
      `germ2_id` INT NULL,
      `germ2_antibiotics` TEXT NULL,
      `germ3_id` INT NULL,
      `germ3_antibiotics` TEXT NULL,
      FOREIGN KEY (`test_id`) REFERENCES `lab_tests`(`id`) ON DELETE CASCADE
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
    """
]

try:
    with conn.cursor() as cursor:
        for q in queries:
            cursor.execute(q)
        print("Recreated lis_microbiology_results table successfully.")
    conn.commit()
finally:
    conn.close()
