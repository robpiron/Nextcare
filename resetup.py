import json
import urllib.request
import os

config_path = "config.json"
if os.path.exists(config_path):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Map config.json structure to setup-db expectations
    setup_payload = {
        "db_host": config.get("db_host", "localhost"),
        "db_port": int(config.get("db_port", 3306)),
        "db_name": config.get("db_name", "nextcare_db"),
        "db_user": config.get("db_user", "root"),
        "db_pass": config.get("db_pass", ""),
        "lis_export_path": config.get("lis_export_path", r"C:\NextCare_LIS_Exchange\export"),
        "lis_import_path": config.get("lis_import_path", r"C:\NextCare_LIS_Exchange\import")
    }

    url = "http://127.0.0.1:8000/api/setup-db"
    data = json.dumps(setup_payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            print("Response:", res_data)
    except Exception as e:
        print("Error connecting to server to perform setup:", str(e))
else:
    print("config.json not found, setup cannot be automated.")
