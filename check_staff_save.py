with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
idx = content.find("document.getElementById('form-add-staff')")
if idx != -1:
    print(content[idx:idx+1500])
else:
    # try searching submit event on form
    print("Not found by ID. Searching for submit events related to staff:")
    for match in re.finditer(r'form-add-staff', content):
        start = max(0, match.start() - 100)
        print(content[start:start+400])
        print("-" * 50)
