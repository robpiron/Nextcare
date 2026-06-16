with open('server.py', 'r', encoding='utf-8') as f:
    for _ in range(50):
        print(f.readline().strip())
