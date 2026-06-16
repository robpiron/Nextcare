with open('server.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'schema.sql' in line or 'initialize' in line.lower() or 'execute' in line.lower():
            if 'db-sync-table' not in line:
                print(f"{idx}: {line.strip()}")
