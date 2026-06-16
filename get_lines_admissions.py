with open('schema.sql', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(400, 440):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
