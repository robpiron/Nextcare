with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="tab-hris"')
if idx != -1:
    print(html[idx + 1800:idx + 3800])
else:
    print("tab-hris NOT found")
