with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

sections = [
    'tab-ssn-billing', 'tab-fse-transmissions', 'tab-sts-transmission'
]

for sec in sections:
    idx = html.find(f'id="{sec}"')
    if idx == -1:
        print(f"Section {sec} not found")
        continue
    
    next_idx = len(html)
    for s in ['tab-ssn-billing', 'tab-fse-transmissions', 'tab-sts-transmission', 'tab-doctor-compensations', 'tab-license']:
        if s != sec:
            s_idx = html.find(f'id="{s}"')
            if s_idx > idx and s_idx < next_idx:
                next_idx = s_idx
    
    sec_content = html[idx:next_idx]
    print(f"\n======================================")
    print(f"DETAILS FOR SECTION: {sec}")
    print(f"======================================")
    
    # Print the clean HTML markup of the section
    print(sec_content[:3000])
    if len(sec_content) > 3000:
        print("... [TRUNCATED SECTION CONTENT] ...")
        # print last 500 chars
        print(sec_content[-500:])
