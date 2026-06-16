with open('app.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'showTab' in line or 'switchTab' in line or 'loadActiveTab' in line or 'tab-reporting' in line:
            print(f"{idx}: {line.strip()}")
