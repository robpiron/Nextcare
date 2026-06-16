with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if "payment_status:" in line and "paid" in line.lower() and "unpaid" not in line.lower():
            print(f"Line {idx}: {line.strip()}")
            for i in range(max(0, idx-5), min(len(lines), idx+5)):
                print(f"  {i+1}: {lines[i]}", end="")
