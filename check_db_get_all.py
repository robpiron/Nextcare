with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('def handle_db_get_all(')
if idx != -1:
    print(content[idx:idx+1500])
else:
    print("handle_db_get_all not found in server.py")
