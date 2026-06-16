with open('schema.sql', 'r', encoding='utf-8') as f:
    content = f.read()

import re
match = re.search(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?`?doctors`?\s*\([\s\S]*?\);', content, re.IGNORECASE)
if match:
    print(match.group(0))
else:
    print("doctors table definition NOT found")
