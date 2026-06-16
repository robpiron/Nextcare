with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="modal-whats-new"')
if idx != -1:
    print(html[idx:idx+3500])
else:
    print("modal-whats-new not found")
