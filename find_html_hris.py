with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'sub-content-ris-' in line:
        print(f"{idx+1}: {line.strip()}")
