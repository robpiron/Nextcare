with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="checkin-listino"' in line:
        for j in range(idx - 1, idx + 6):
            print(f'{j+1}: {lines[j].strip()}')
        break
