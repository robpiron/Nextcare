with open('style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(1770, 1870):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
