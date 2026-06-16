with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer('form-add-staff', content)]
print(f"Found 'form-add-staff' {len(matches)} times")
for m in matches:
    print(f"Match at index {m}:")
    print(content[max(0, m-200):m+1300])
    print("=" * 60)
