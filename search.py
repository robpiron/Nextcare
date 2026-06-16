with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="tab-notifications"')
if idx != -1:
    print("=== NOTIFICATIONS TAB ===")
    print(content[idx:idx+2000])
else:
    print("tab-notifications not found")
