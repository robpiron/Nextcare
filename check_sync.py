with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('syncFromMySQL')
if idx != -1:
    print(content[idx:idx+1500])
else:
    print("syncFromMySQL not found")
