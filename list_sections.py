with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
matches = re.findall(r'<section\s+id="([^"]+)"', html)
print(matches)
