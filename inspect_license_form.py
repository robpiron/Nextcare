with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="form-license-activation"')
if idx != -1:
    print(html[idx:idx+1500])
else:
    print("form-license-activation not found in index.html")
