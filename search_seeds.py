import json
import os

for filename in ['ris_visite_services_seed.json', 'lis_services_seed.json']:
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # check if any item has 'alert_note'
            has_alert = any('alert_note' in item for item in data)
            print(f"File {filename} has alert_note keys: {has_alert}")
