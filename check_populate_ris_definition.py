with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('function populateDropdownsRIS(')
if idx == -1:
    idx = content.find('populateDropdownsRIS =')
if idx == -1:
    idx = content.find('populateDropdownsRIS')

if idx != -1:
    print(content[idx:idx+1500])
else:
    print("populateDropdownsRIS definition not found")
