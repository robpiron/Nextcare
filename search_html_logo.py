with open('index.html', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'logo' in line.lower() or 'sidebar' in line.lower() or 'brand' in line.lower():
            if not ('logo_base64' in line):
                print(f"{idx}: {line.strip()}")
