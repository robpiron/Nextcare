import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all divs containing 'modal-' in their id
modal_divs = re.findall(r'<div\s+[^>]*id=["\'](modal-[a-zA-Z0-9_-]+)["\'][^>]*>', content)
print("Modals found:")
for m in modal_divs:
    print(f"  - {m}")
