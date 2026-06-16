with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find("localStorage.setItem('nextcare_logged_in_user'")
if idx != -1:
    print(content[idx-200:idx+1500])
else:
    print("Not found")
