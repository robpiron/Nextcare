with open('app.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'checkSystemStatus' in line or 'function checkSystemStatus' in line:
            print(f"{idx}: {line.strip()}")
