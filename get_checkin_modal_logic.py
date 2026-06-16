with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function openCheckinModal' in line:
        for j in range(idx, idx + 40):
            print(f'{j+1}: {lines[j].strip()}')
        break
