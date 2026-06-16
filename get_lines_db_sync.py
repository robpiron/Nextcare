with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(1116, 1180):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
