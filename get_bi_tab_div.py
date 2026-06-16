with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="tab-bi-dashboard"')
if idx != -1:
    print(html[idx:idx+1500])
else:
    print("tab-bi-dashboard NOT found in index.html")
