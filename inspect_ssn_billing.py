with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# find any occurrence of ssn or impegnative or ricette in section elements
matches = re.findall(r'<section\s+id="([^"]*)"[^>]*>', html)
print("All section IDs in index.html:")
for m in matches:
    if 'ssn' in m or 'recipe' in m or 'billing' in m or 'ricette' in m:
        print(f"Matched section ID: {m}")
        idx = html.find(f'id="{m}"')
        print(html[idx:idx+1200])
        print("="*60)
