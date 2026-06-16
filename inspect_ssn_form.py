with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="tab-ssn-billing"')
if idx != -1:
    snippet = html[idx+3000:idx+6000]
    print("=== tab-ssn-billing table section ===")
    print(snippet)
