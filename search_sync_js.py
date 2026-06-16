with open('app.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'sync' in line.lower() or 'db-sync-table' in line:
            print(f"{idx}: {line.strip()}")
