with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if 'id="tab-patients"' in line or 'tab-patients' in line:
            print(f"Line {idx}: {line.strip()}")
            for i in range(max(0, idx-2), min(len(lines), idx+15)):
                print(f"  {i+1}: {lines[i]}", end="")
