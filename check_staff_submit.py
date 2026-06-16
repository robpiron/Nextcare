with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

import re
idx = content.find('form-add-staff')
if idx != -1:
    print(content[idx-200:idx+1500])
else:
    print("form-add-staff not found in app.js")
