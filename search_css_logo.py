with open('style.css', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if '.logo' in line or 'sidebar-header' in line or 'logo-icon' in line:
            print(f"{idx}: {line.strip()}")
