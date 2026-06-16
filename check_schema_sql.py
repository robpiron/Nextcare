with open('schema.sql', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('CREATE TABLE `doctors`')
if idx != -1:
    print(content[idx:idx+1000])
else:
    print("doctors table definition not found in schema.sql")
