with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
scripts = re.findall(r'<script\s+src="([^"]*)"', html)
print("Scripts imported in index.html:")
for s in scripts:
    print(s)
