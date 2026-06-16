with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('window.loadRolePermissions =')
if idx != -1:
    print(content[idx+2000:idx+4500])
else:
    print("loadRolePermissions not found")
