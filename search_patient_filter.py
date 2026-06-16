with open('app.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'patient' in line.lower() and ('filter' in line.lower() or 'search' in line.lower()):
            if 'function' in line or '=>' in line or 'const ' in line or 'let ' in line:
                print(f"Line {idx}: {line.strip()[:100]}")
