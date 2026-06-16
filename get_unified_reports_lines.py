with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="tab-unified-reports"' in line:
        print(f"Line: {idx + 1}")
        for j in range(idx - 1, idx + 10):
            print(f"{j+1}: {lines[j].strip()}")
        break
