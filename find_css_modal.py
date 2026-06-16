with open('style.css', 'r', encoding='utf-8') as f:
    lines = f.readlines()

in_modal = False
for idx, line in enumerate(lines, 1):
    if '.modal-box' in line:
        in_modal = True
    if in_modal:
        print(f"{idx}: {line.rstrip()}")
        if '}' in line:
            in_modal = False
