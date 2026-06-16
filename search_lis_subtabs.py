with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if 'id="subtab-lis-acceptances"' in line or 'id="lis-acceptances-content"' in line or 'id="lis-samples-content"' in line or 'id="subtab-lis-samples"' in line:
            print(f"Line {idx}: {line.strip()}")
            for i in range(max(0, idx-1), min(len(lines), idx+30)):
                print(f"  {i+1}: {lines[i]}", end="")
