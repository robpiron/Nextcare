with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

modals = [
    'modal-add-patient', 'modal-add-appointment', 'modal-checkin-appointment', 
    'modal-add-staff', 'modal-add-claim', 'modal-add-company', 
    'modal-add-insurance', 'modal-whats-new', 'modal-add-ris'
]

print("=== Modals in index.html ===")
for modal in modals:
    # Find modal container and modal-box class
    pattern = rf'id="{modal}"[^>]*>[\s\S]*?<div\s+class="([^"]*)"'
    match = re.search(pattern, html)
    if match:
        print(f"Modal {modal}: class = '{match.group(1)}'")
    else:
        # print first few lines of the modal container
        idx = html.find(f'id="{modal}"')
        if idx != -1:
            print(f"Modal {modal} found at index {idx}, first 150 chars: {html[idx:idx+150]!r}")
        else:
            print(f"Modal {modal} NOT found")

print("\n=== Tabs in index.html ===")
for tab in ['tab-license', 'license']:
    idx = html.find(tab)
    if idx != -1:
        print(f"'{tab}' found at index {idx}, snippet: {html[max(0, idx-100):idx+300]!r}")
    else:
        print(f"'{tab}' NOT found")
