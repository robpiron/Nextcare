with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

import re
matches = [m.start() for m in re.finditer('sendSimulatedEmail', code)]
print(f"Occurrences of 'sendSimulatedEmail': {len(matches)}")
for idx, m in enumerate(matches):
    start = max(0, m - 100)
    end = min(len(code), m + 150)
    print(f"{idx}: ... {code[start:end]} ...")
