with open('server.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for idx in range(4719, 4770):
    print(f'{idx+1}: {lines[idx].strip()}')
