import json
import urllib.request
import re
import os

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
    
    # Find all table arrays in SEED_DATA
    # e.g., staff: [ ... ], or audit_logs: [ ... ]
    array_matches = list(re.finditer(r'^\s*(\w+):\s*\[', seed_block, re.MULTILINE))
    
    parsed_seeds = {}
    for idx, am in enumerate(array_matches):
        key_name = am.group(1)
        arr_start = am.end() - 1
        
        # Determine the end of this array in seed_block
        arr_brace_count = 1
        arr_end = arr_start + 1
        while arr_brace_count > 0 and arr_end < len(seed_block):
            c = seed_block[arr_end]
            if c == '[':
                arr_brace_count += 1
            elif c == ']':
                arr_brace_count -= 1
            arr_end += 1
            
        arr_content = seed_block[arr_start:arr_end]
        
        # Let's convert this JS array syntax to JSON
        # Remove comments
        arr_content_clean = re.sub(r'//.*', '', arr_content)
        # Convert keys: key: to "key":
        arr_content_clean = re.sub(r'(\w+):', r'"\1"', arr_content_clean)
        # Convert single quotes to double quotes
        arr_content_clean = re.sub(r"'([^']*)'", r'"\1"', arr_content_clean)
        # Remove trailing commas inside objects
        arr_content_clean = re.sub(r',\s*}', '}', arr_content_clean)
        # Remove trailing commas inside arrays
        arr_content_clean = re.sub(r',\s*\]', ']', arr_content_clean)
        
        try:
            items = json.loads(arr_content_clean)
            parsed_seeds[key_name] = items
        except Exception as e:
            # If parsing fails, try using regex to extract individual objects and parse them
            obj_matches = re.finditer(r'\{([^{}]*)\}', arr_content)
            items = []
            for om in obj_matches:
                obj_str = "{" + om.group(1).strip() + "}"
                obj_str = re.sub(r'//.*', '', obj_str)
                obj_str = re.sub(r'(\w+):', r'"\1":', obj_str)
                obj_str = re.sub(r"'([^']*)'", r'"\1"', obj_str)
                obj_str = re.sub(r',\s*}', '}', obj_str)
                try:
                    obj = json.loads(obj_str)
                    items.append(obj)
                except Exception:
                    pass
            if items:
                parsed_seeds[key_name] = items

    print("Parsed tables count:", len(parsed_seeds))
    
    for table, rows in parsed_seeds.items():
        payload = {
            "table_name": table,
            "rows": rows
        }
        url = "http://127.0.0.1:8000/api/db-sync-table"
        data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                res = json.loads(response.read().decode('utf-8'))
                if not res.get("success"):
                    print(f"Sync actual {table} FAILED: {res.get('error')}")
                else:
                    print(f"Sync actual {table} SUCCESS ({len(rows)} rows)")
        except urllib.error.HTTPError as he:
            err_body = he.read().decode('utf-8')
            print(f"HTTP Error sync actual {table}: {he.code} - {err_body}")
        except Exception as e:
            print(f"Error sync actual {table}: {str(e)}")
else:
    print("Could not find SEED_DATA")
