with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.finditer(r'<button[^>]*?onclick="switchTab\(\'([^\']+)\'\)"[^>]*?>(.*?)</button>', html, re.DOTALL)
for m in matches:
    print(f"Tab ID: {m.group(1)}, Content: {m.group(2).strip()}")
