with open('schema.sql', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'invoices' in line.lower() and 'table' in line.lower():
        print(f"Found table match at line {idx}: {line.strip()}")
        # print 30 lines after this line
        for offset in range(1, 35):
            if idx + offset < len(lines):
                print(f"{idx+offset}: {lines[idx+offset-1].strip()}")
