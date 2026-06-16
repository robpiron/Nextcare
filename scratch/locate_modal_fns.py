with open('portal_template.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'function openModal' in line or 'function closeModal' in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print some lines after
        for i in range(idx, min(len(lines), idx + 8)):
            print(f"  {i+1}: {lines[i].rstrip()}")
