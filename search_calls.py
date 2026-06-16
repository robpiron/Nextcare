with open('server.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'db-sync-table' in line or 'def handle_db_sync_table' in line:
            print(f"{idx}: {line.strip()[:140]}")
