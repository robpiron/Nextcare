with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.finditer(r'<section[^>]*?id="([^"]+)"[^>]*?class="tab-content"', html)
for m in matches:
    print(f"ID: {m.group(1)} at position {m.start()}")
