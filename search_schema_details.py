with open('schema.sql', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def print_table_def(table_name):
    in_table = False
    for idx, line in enumerate(lines, 1):
        if f'CREATE TABLE IF NOT EXISTS `{table_name}`' in line or f'CREATE TABLE `{table_name}`' in line:
            in_table = True
        if in_table:
            print(f"{idx}: {line.strip()}")
            if ');' in line or ');' in line.strip():
                if not ('CREATE TABLE' in line):
                    in_table = False
                    print("-" * 40)

print_table_def('medical_services')
print_table_def('lab_samples')
