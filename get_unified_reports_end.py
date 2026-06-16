with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for idx, line in enumerate(lines):
    if 'id="tab-unified-reports"' in line:
        found = True
    if found and idx > 1517:
        if '<section' in line:
            print(f"End line index: {idx + 1}")
            for j in range(idx - 5, idx + 5):
                print(f"{j+1}: {lines[j].strip()}")
            break
