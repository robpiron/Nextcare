import re

with open('portal_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

matches = re.findall(r'id=["\'](modal-[a-zA-Z0-9_-]+)["\']', content)
print("Modals found in portal_template.html:")
for m in matches:
    print(f" - {m}")
