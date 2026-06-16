with open('schema.sql', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('CREATE TABLE `doctors`')
if idx == -1:
    idx = content.find('CREATE TABLE IF NOT EXISTS `doctors`')
if idx == -1:
    idx = content.find('doctors')

if idx != -1:
    print(content[idx:idx+1500])
else:
    print("doctors not found in schema.sql")
