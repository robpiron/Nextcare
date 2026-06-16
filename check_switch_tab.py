with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Look for switchTab function
idx = content.find('switchTab')
if idx != -1:
    print("=== switchTab definition ===")
    print(content[idx:idx+1500])
else:
    # search for document.querySelectorAll('.nav-item') or similar
    print("switchTab not found directly. Searching for tab events:")
    for match in re.finditer(r'tab-content', content):
        start = max(0, match.start() - 100)
        print(content[start:start+300])
        print("-" * 50)
