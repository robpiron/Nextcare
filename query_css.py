with open('style.css', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if '--' in line and '{' in line or ':' in line:
            if idx < 50: # just get the root variables
                print(f"{idx}: {line.strip()}")
