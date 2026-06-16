with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx, line in enumerate(lines):
    if "case 'hris':" in line or 'case "hris":' in line:
        for j in range(idx - 2, idx + 40):
            print(f'{j+1}: {lines[j].strip()}')
        break
