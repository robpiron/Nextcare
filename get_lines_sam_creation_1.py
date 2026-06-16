with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(4490, 4530):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
