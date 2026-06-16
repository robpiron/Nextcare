with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

def print_section(section_id, max_len=3000):
    idx = html.find(f'id="{section_id}"')
    if idx != -1:
        print(f"=== SECTION: {section_id} ===")
        print(html[idx:idx+max_len])
    else:
        print(f"=== SECTION: {section_id} NOT FOUND ===")

print_section("modal-add-staff", 6000)
print_section("tab-license", 4000)
print_section("modal-whats-new", 2000)
