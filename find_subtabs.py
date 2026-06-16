with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.findall(r'<div[^>]*?class="sub-tabs-container".*?</div>', html, re.DOTALL)
for m in matches:
    print(m)
    print("-" * 20)
