with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer('login', content, re.IGNORECASE)]
print(f"Found 'login' {len(matches)} times")
for m in matches:
    snippet = content[max(0, m-200):m+800]
    if 'success' in snippet.lower() or 'password' in snippet.lower() or 'modal-whats-new' in snippet.lower():
        print(f"Match at index {m}:")
        print(snippet)
        print("="*60)
