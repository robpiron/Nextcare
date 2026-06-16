with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Find all occurrences of @app.route or @app.post or @app.get or similar in server.py
# Or let's look for @app.route
endpoints = re.findall(r'@app\.route\(\'([^\']*)\'', content)
endpoints += re.findall(r'@app\.route\("([^"]*)"', content)

print("=== Endpoints in server.py ===")
for ep in sorted(endpoints):
    if any(k in ep for k in ['license', 'fse', 'sts', 'recipe', 'compensation', 'ssn', 'settings', 'doctor']):
        print(ep)
