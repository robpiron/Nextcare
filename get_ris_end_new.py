with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="tab-unified-reports"' in line:
        for j in range(idx - 6, idx + 2):
            print(f"{j+1}: {lines[j].strip()}")
        break
