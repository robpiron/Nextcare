with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

sections = [
    'tab-ssn-billing', 'tab-fse-transmissions', 'tab-sts-transmission', 
    'tab-doctor-compensations', 'tab-license'
]

for sec in sections:
    idx = html.find(f'id="{sec}"')
    if idx != -1:
        print(f"\n=== SECTION {sec} ===")
        # print first 2000 chars of the section
        print(html[idx:idx+2000])
    else:
        # try search by substring in case ID is slightly different
        print(f"\n=== SECTION {sec} NOT FOUND (searching substring) ===")
        matches = [m.start() for m in re.finditer(sec.split('-')[1], html)]
        for m in matches[:3]:
            print(f"Match for '{sec.split('-')[1]}' snippet: {html[m-50:m+200]!r}")
