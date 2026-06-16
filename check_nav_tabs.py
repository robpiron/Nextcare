with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
nav_items = re.findall(r'<a\s+[^>]*class="nav-item"[^>]*data-tab="([^"]*)"[^>]*>([\s\S]*?)<\/a>', html)
print("=== Nav Items in index.html ===")
for tab, content in nav_items:
    label = re.sub('<[^<]+?>', '', content).strip()
    print(f"Tab: '{tab}' -> Label: '{label}'")
