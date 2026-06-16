import glob

for f in glob.glob('*.html') + glob.glob('*.js'):
    with open(f, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    for idx, line in enumerate(lines):
        if 'openModal' in line and ('=' in line or 'function' in line):
            print(f"{f}:{idx+1}: {line.strip()}")
