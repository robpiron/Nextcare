with open('portal_template.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="modal-add-patient"' in line:
        print(f"Line {idx+1}: {line.strip()}")
        # print some lines before and after
        start = max(0, idx - 10)
        end = min(len(lines), idx + 20)
        for i in range(start, end):
            print(f"  {i+1}: {lines[i].rstrip()}")
        break
