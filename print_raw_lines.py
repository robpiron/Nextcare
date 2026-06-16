with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'id="st-comp-type"' in line:
        print(f"Match at line {idx}: {line.strip()}")
        # print next 20 lines
        for offset in range(1, 20):
            print(f"Line {idx+offset}: {lines[idx+offset].strip()}")
        break
