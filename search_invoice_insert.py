with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'invoices.push' in line or '.push(' in line and ('invoice_number' in line or 'amount_due' in line):
        print(f"Match at line {idx}: {line.strip()}")
        # print subsequent lines to show object keys
        for i in range(1, 15):
            if idx + i < len(lines):
                print(f"{idx+i}: {lines[idx+i-1].strip()}")
