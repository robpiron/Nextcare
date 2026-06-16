with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="tab-hris"' in line:
        # print around
        for j in range(idx - 2, idx + 100):
            print(f'{j+1}: {lines[j].strip()}')
        break
