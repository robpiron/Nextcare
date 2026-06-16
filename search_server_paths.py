with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re

paths = re.findall(r'path\.startswith\(\'([^\']*)\'\)', content)
paths += re.findall(r'path\.startswith\("([^"]*)"\)', content)
paths += re.findall(r'path\s*==\s*\'([^\']*)\'', content)
paths += re.findall(r'path\s*==\s*"([^"]*)"', content)

print("=== Found paths in server.py ===")
for p in sorted(list(set(paths))):
    print(p)
