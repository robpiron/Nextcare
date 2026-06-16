with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find("document.getElementById('form-add-staff').addEventListener('submit'")
if idx != -1:
    print(content[idx:idx+4500])
else:
    print("Not found")
