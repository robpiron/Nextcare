import json
import urllib.request
import re

with open('app.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

start_idx = js_content.find('const SEED_DATA = {')
if start_idx == -1:
    print("Could not find SEED_DATA")
    exit()

brace_count = 1
idx = start_idx + len('const SEED_DATA = {')
block_start = idx
while brace_count > 0 and idx < len(js_content):
    if js_content[idx] == '{':
        brace_count += 1
    elif js_content[idx] == '}':
        brace_count -= 1
    idx += 1
seed_block = js_content[block_start:idx-1]

# Extract array positions
array_positions = []
arr_matches = list(re.finditer(r'^\s*(\w+):\s*\[', seed_block, re.MULTILINE))
for match in arr_matches:
    key = match.group(1)
    start_pos = match.end() - 1
    bracket_count = 1
    p = start_pos + 1
    while bracket_count > 0 and p < len(seed_block):
        if seed_block[p] == '[':
            bracket_count += 1
        elif seed_block[p] == ']':
            bracket_count -= 1
        p += 1
    arr_str = seed_block[start_pos:p]
    array_positions.append((key, arr_str))

for key, arr_str in array_positions:
    # Remove comments
    clean = re.sub(r'//.*', '', arr_str)
    
    # Placeholder strings to avoid matching inside quotes
    strings = []
    def save_string(m):
        strings.append(m.group(0))
        return f"__STR_PLACEHOLDER_{len(strings)-1}__"
    
    # Replace all double-quoted and single-quoted strings
    clean = re.sub(r'"[^"\\]*(?:\\.[^"\\]*)*"', save_string, clean)
    clean = re.sub(r"'[^'\\]*(?:\\.[^'\\]*)*'", save_string, clean)
    
    # Now replace keys (word followed by colon)
    # A key is a word character sequence followed by a colon
    clean = re.sub(r'\b([a-zA-Z_]\w*)\s*:', r'"\1":', clean)
    
    # Restore strings
    for i, s in enumerate(strings):
        # Convert single quoted saved strings to double quotes for JSON compliance
        if s.startswith("'") and s.endswith("'"):
            s_content = s[1:-1].replace('"', '\\"')
            s = f'"{s_content}"'
        clean = clean.replace(f"__STR_PLACEHOLDER_{i}__", s)
    
    # Clean trailing commas
    clean = re.sub(r',\s*}', '}', clean)
    clean = re.sub(r',\s*\]', ']', clean)
    
    # Remove null fields if they are plain words like null (JSON compliant)
    # in JS, null, true, false don't have quotes. They are JSON compliant anyway.
    
    try:
        data = json.loads(clean)
        
        # Post to sync endpoint
        payload = {
            "table_name": key,
            "rows": data
        }
        url = "http://127.0.0.1:8000/api/db-sync-table"
        req_data = json.dumps(payload).encode('utf-8')
        req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
        
        try:
            with urllib.request.urlopen(req) as resp:
                res = json.loads(resp.read().decode('utf-8'))
                if res.get("success"):
                    print(f"Table '{key}' synced successfully. ({len(data)} rows)")
                else:
                    print(f"Table '{key}' sync FAILED: {res.get('error')}")
        except urllib.error.HTTPError as he:
            print(f"Table '{key}' sync HTTP Error {he.code}: {he.read().decode('utf-8')}")
        except Exception as e:
            print(f"Table '{key}' sync error: {str(e)}")
            
    except Exception as je:
        print(f"Failed to parse array for '{key}': {str(je)}")
