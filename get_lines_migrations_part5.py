with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(4980, 5050):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
