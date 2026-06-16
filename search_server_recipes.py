with open('server.py', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'ssn_recipes' in line or 'ssn_exemptions' in line:
            print(f"{idx}: {line.strip()[:120]}")
