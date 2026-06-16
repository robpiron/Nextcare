with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('const DB =')
if idx != -1:
    print(content[idx+2000:idx+4000])
else:
    print("DB definition not found")
