with open('app.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'const SEED_DATA' in line or 'SEED_DATA =' in line:
            print(f"{idx}: {line.strip()}")
