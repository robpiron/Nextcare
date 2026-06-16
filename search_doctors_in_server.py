with open('server.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'doctors' in line.lower():
            print(f"{idx}: {line.strip()[:120]}")
