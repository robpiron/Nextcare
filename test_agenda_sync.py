import pymysql
import json

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

try:
    with conn.cursor() as cursor:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        cursor.execute("DELETE FROM `doctor_agendas` WHERE `id` = 999")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        
        # Test inserting with doctor_id = None
        sql = "INSERT INTO `doctor_agendas` (`id`, `doctor_id`, `start_date`, `end_date`, `active_days`, `slot_duration_minutes`, `name`, `reporting_doctor_ids`, `time_slots`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor.execute(sql, (999, None, '2026-06-01', '2026-06-30', 'Monday,Wednesday', 30, 'DIAGNOSTICA GENERICA', '[1, 2]', '[{"start": "08:00", "end": "14:00"}]'))
        
        conn.commit()
        print("Insert successful!")
        
        cursor.execute("DELETE FROM `doctor_agendas` WHERE `id` = 999")
        conn.commit()
        print("Cleanup successful!")
finally:
    conn.close()
