with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

print("=== modal-add-staff contents ===")
idx_staff = html.find('id="modal-add-staff"')
if idx_staff != -1:
    snippet = html[idx_staff:idx_staff+6000]
    # search for keywords like compenso, commissione, doctor_compensation or trigger
    for kw in ['compenso', 'compensation', 'trigger', 'payout', 'valore']:
        if kw in snippet.lower():
            print(f"Found keyword '{kw}' in modal-add-staff snippet!")
    print("Snippet around doctor section:")
    doc_idx = snippet.find('id="staff-specialization"')
    if doc_idx != -1:
        print(snippet[doc_idx-200:doc_idx+2000])
    else:
        print("staff-specialization not found in first 6000 chars of modal-add-staff")
else:
    print("modal-add-staff not found")

print("\n=== modal-add-ris contents ===")
idx_ris = html.find('id="modal-add-ris"')
if idx_ris != -1:
    snippet_ris = html[idx_ris:idx_ris+4000]
    print("Snippet:")
    print(snippet_ris[:1500])
    # check for ris-tsrm, ris-reporting-doctor, ris-requester
    for id_val in ['ris-tsrm', 'ris-reporting-doctor', 'ris-doctor', 'ris-requester']:
        if id_val in snippet_ris:
            print(f"Found id '{id_val}' in modal-add-ris!")
        else:
            print(f"id '{id_val}' NOT found in modal-add-ris")
else:
    print("modal-add-ris NOT found")
