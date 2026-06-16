with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="hris-companies-pane"')
if idx != -1:
    print(html[idx:idx+2500])
else:
    print("hris-companies-pane NOT found")
