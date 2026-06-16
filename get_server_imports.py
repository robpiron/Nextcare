with open('server.py', 'r', encoding='utf-8') as f:
    for idx in range(100):
        line = f.readline()
        if not line:
            break
        print(f'{idx+1}: {line.strip()}')
