with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'switchtab' in line.lower():
        print(f"{idx+1}: {line.strip()}")
