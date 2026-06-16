with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="tab-hris"')
if idx != -1:
    print(html[idx:idx+2500])
else:
    print("tab-hris NOT found")
