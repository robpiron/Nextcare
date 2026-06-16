import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

mid = 'modal-edit-lis-acceptance'
start_match = re.search(r'<div\s+[^>]*id=["\']' + mid + r'["\'][^>]*>', content)
if start_match:
    start_pos = start_match.start()
    div_count = 1
    pos = start_match.end()
    while div_count > 0 and pos < len(content):
        if content[pos:pos+4] == '<div':
            div_count += 1
            pos += 4
        elif content[pos:pos+5] == '</div':
            div_count -= 1
            pos += 5
        else:
            pos += 1
    modal_html = content[start_pos:pos]
    print(modal_html[:1500])
else:
    print("Not found")
