with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines, 1):
    if 'invoice_number:' in line or 'is_insurance_invoice:' in line:
        print(f"Match at line {idx}: {line.strip()}")
        # print subsequent lines
        for i in range(1, 10):
            if idx + i < len(lines):
                print(f"{idx+i}: {lines[idx+i-1].strip()}")
