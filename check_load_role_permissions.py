with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('window.loadRolePermissions =')
if idx == -1:
    idx = content.find('loadRolePermissions =')
if idx == -1:
    idx = content.find('function loadRolePermissions')

if idx != -1:
    print(content[idx:idx+2000])
else:
    print("loadRolePermissions not found")
