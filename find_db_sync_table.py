with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'def handle_db_sync_table' in line:
        for j in range(idx, idx + 80):
            print(f'{j+1}: {lines[j].strip()}')
        break
