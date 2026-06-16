with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

if 'toggleRisRequester' in content:
    print("toggleRisRequester found!")
    idx = content.find('toggleRisRequester')
    print(content[idx:idx+500])
else:
    print("toggleRisRequester NOT found")
