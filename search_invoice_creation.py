with open('app.js', 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f, 1):
        if 'invoices.push(' in line or 'amount_due' in line:
            # print the matching line and the surrounding 15 lines
            print(f"Match at line {idx}: {line.strip()}")
