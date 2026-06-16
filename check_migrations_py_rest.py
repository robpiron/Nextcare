with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('def run_db_migrations(')
if idx != -1:
    print(content[idx+2500:idx+5500])
else:
    print("run_db_migrations not found in server.py")
