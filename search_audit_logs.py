with open('schema.sql', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_table = False
for idx, line in enumerate(lines, 1):
    if 'CREATE TABLE IF NOT EXISTS `audit_logs`' in line or 'CREATE TABLE `audit_logs`' in line:
        in_table = True
    if in_table:
        print(f"{idx}: {line.strip()}")
        if ');' in line or ');' in line.strip():
            if not ('CREATE TABLE' in line):
                in_table = False
