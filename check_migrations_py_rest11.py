with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('def run_db_migrations(')
if idx != -1:
    print(content[idx+40000:idx+44500])
else:
    print("run_db_migrations not found in server.py")
