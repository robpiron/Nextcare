with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('customCheckinSubmit =')
if idx != -1:
    print(content[idx:idx+3000])
else:
    print("customCheckinSubmit not found")
