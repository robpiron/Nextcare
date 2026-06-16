with open('index.html', encoding='utf-8') as f:
    content = f.read()

import re
m = re.search(r'id=["\']modal-lis-print-prompt["\']', content)
if m:
    # Find the containing div
    start = content.rfind('<div', 0, m.start())
    # Count matching divs
    div_count = 1
    pos = m.end()
    while div_count > 0 and pos < len(content):
        if content[pos:pos+4] == '<div':
            div_count += 1
            pos += 4
        elif content[pos:pos+5] == '</div':
            div_count -= 1
            pos += 5
        else:
            pos += 1
    print(content[start:pos])
else:
    print("Not found")
