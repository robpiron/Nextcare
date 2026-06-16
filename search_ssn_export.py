with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

if 'exportSsnFlussi' in content:
    print("exportSsnFlussi found!")
    idx = content.find('exportSsnFlussi')
    print(content[idx:idx+500])
else:
    print("exportSsnFlussi NOT found")
