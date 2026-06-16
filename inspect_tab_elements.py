with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

sections = [
    'tab-ssn-billing', 'tab-fse-transmissions', 'tab-sts-transmission', 
    'tab-doctor-compensations', 'tab-license'
]

for sec in sections:
    idx = html.find(f'id="{sec}"')
    if idx == -1:
        print(f"Section {sec} not found")
        continue
    
    # Extract the full section block
    # Simple search for the closing section tag.
    # Note: since there can be nested sections (though unlikely), we will just scan for the end of the section by balance of tags, or just search next </section> before the next main tab section.
    next_idx = len(html)
    for s in sections:
        if s != sec:
            s_idx = html.find(f'id="{s}"')
            if s_idx > idx and s_idx < next_idx:
                next_idx = s_idx
    
    sec_content = html[idx:next_idx]
    print(f"\n======================================")
    print(f"ELEMENTS IN SECTION: {sec}")
    print(f"======================================")
    
    # Find all ids
    ids = re.findall(r'id="([^"]*)"', sec_content)
    print(f"IDs: {ids}")
    
    # Find all table bodies or tables
    tables = re.findall(r'<table[^>]*>[\s\S]*?<\/table>', sec_content)
    print(f"Tables count: {len(tables)}")
    for tidx, table in enumerate(tables):
        # find the table headers
        headers = re.findall(r'<th[^>]*>([\s\S]*?)<\/th>', table)
        headers_cleaned = [re.sub('<[^<]+?>', '', h).strip() for h in headers]
        print(f"  Table {tidx+1} headers: {headers_cleaned}")
        # find tbody id if any
        tbody_id = re.search(r'<tbody[^>]*id="([^"]*)"', table)
        if tbody_id:
            print(f"  Table {tidx+1} tbody id: {tbody_id.group(1)}")
        else:
            print(f"  Table {tidx+1} tbody id: NOT FOUND")

    # Find all buttons/forms
    onclicks = re.findall(r'onclick="([^"]*)"', sec_content)
    print(f"Onclicks: {onclicks}")
    onsubmits = re.findall(r'onsubmit="([^"]*)"', sec_content)
    print(f"Onsubmits: {onsubmits}")
