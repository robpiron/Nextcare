with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    for idx, line in enumerate(lines, 1):
        if "insert('invoices'" in line or 'insert("invoices"' in line or 'DB.insert(\'invoices\'' in line:
            print(f"Line {idx}: {line.strip()}")
            # print surrounding 5 lines
            for i in range(max(0, idx-5), min(len(lines), idx+5)):
                print(f"  {i+1}: {lines[i]}", end="")
