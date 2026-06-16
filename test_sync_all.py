import json
import urllib.request
import os
import re

# Extract SEED_DATA from app.js
content = open('app.js', encoding='utf-8').read()

start_match = re.search(r'const\s+SEED_DATA\s*=\s*\{', content)
if start_match:
    start_idx = start_match.end() - 1
    brace_count = 1
    end_idx = start_idx + 1
    while brace_count > 0 and end_idx < len(content):
        char = content[end_idx]
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        end_idx += 1
    
    seed_block = content[start_idx:end_idx]
    
    # We can write a simple regex to parse array contents for seed tables
    # Since we only need to test if they fail to sync, we can simulate an empty sync first or send a dummy row
    # Let's extract the actual table lists. Since regex parsing complex JS objects is hard,
    # let's just fetch all table names, then make requests.
    tables = re.findall(r'^\s*(\w+):\s*\[', seed_block, re.MULTILINE)

    print("Tables to test:", tables)

    # Let's send a sync request with an empty row array to test constraints, or with a minimal valid row.
    # Actually, let's read the seed json files or mock rows.
    # To get actual data, let's read the table's seed items if possible, or just send a test.
    # Wait, we can run a simple mock sync request with no rows or with one mock row.
    # But wait, in the server logs:
    # "POST /api/db-sync-table HTTP/1.1" 500
    # Let's check which tables fail when we call sync from the app.
    # Let's make sync requests for all tables with an empty list first.
    for table in tables:
        payload = {
            "table_name": table,
            "rows": []
        }
        url = "http://127.0.0.1:8000/api/db-sync-table"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                if not res.get("success"):
                    print(f"Sync empty {table} failed: {res.get('error')}")
        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8')
            print(f"HTTP Error sync empty {table}: {he.code} - {err_body}")
        except Exception as e:
            print(f"Error sync empty {table}: {str(e)}")

        # Now let's try to sync with actual seed data if we can parse it.
        # But wait! Why does sync fail during runtime?
        # Let's write a python script to parse the SEED_DATA using JS execution or similar,
        # or we can read ris_visite_services_seed.json etc. and test them.
        # Wait, let's look at the error log in detail.
