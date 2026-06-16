with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.finditer(r'class="modal-overlay"[^>]*?id="([^"]+)"', html)
for m in matches:
    print(f"ID: {m.group(1)} at position {m.start()}")
