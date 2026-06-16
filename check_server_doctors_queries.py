with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = re.findall(r'SELECT\s+[\s\S]*?\s+FROM\s+\bdoctors\b[\s\S]*?', content, re.IGNORECASE)
print(f"Found {len(matches)} queries referencing doctors:")
for m in matches[:5]:
    print(m[:300])
    print("-" * 50)
