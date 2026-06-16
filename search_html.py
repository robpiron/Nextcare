with open('index.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'eq-lis' in line or 'lis_file_format' in line or 'lis_socket_format' in line:
            print(f"{idx}: {line.strip()[:140]}")
