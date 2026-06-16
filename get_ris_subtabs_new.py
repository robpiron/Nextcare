with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="btn-sub-ris-exams"' in line:
        for j in range(idx - 2, idx + 12):
            print(f"{j+1}: {lines[j].strip()}")
        break
