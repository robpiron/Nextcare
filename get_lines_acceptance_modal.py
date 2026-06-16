with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(5440, 5520):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
