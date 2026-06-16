with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('loadRolePermissions')
if idx != -1:
    print(content[idx:idx+1500])
else:
    # search for allowed tabs or roles
    print("loadRolePermissions not found. Searching for 'admin' or 'allowedTabs':")
    import re
    matches = re.findall(r'(\b[a-zA-Z_0-9]*allowedTabs\b|\b[a-zA-Z_0-9]*permissions\b)', content)
    print(set(matches))
