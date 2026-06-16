import glob

for f in glob.glob('*.html') + glob.glob('*.js'):
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    if 'function openModal' in content:
        print(f"Defined in {f}")
