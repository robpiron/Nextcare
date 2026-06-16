with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Let's search for tab-reporting-services and print the next 2000 chars of table markup
idx = html.find('id="tab-reporting-services"')
if idx != -1:
    table_idx = html.find('<table', idx)
    if table_idx != -1:
        print("--- Reporting Services Table ---")
        print(html[table_idx:table_idx+1200])

idx_acc = html.find('id="tab-reporting-acceptances"')
if idx_acc != -1:
    table_idx = html.find('<table', idx_acc)
    if table_idx != -1:
        print("--- Reporting Acceptances Table ---")
        print(html[table_idx:table_idx+1200])
