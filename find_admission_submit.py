with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'form-add-admission' in line or 'submit' in line.lower() and 'admission' in line.lower():
        print(f'{idx+1}: {line.strip()}')
