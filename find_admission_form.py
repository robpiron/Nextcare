with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="modal-add-admission"')
if idx != -1:
    print(html[idx:idx + 2500])
else:
    print("Not found")
