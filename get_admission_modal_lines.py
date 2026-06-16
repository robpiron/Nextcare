with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

found = False
for idx, line in enumerate(lines):
    if 'id="modal-add-admission"' in line:
        found = True
        for j in range(idx, idx + 40):
            print(f'{j+1}: {lines[j].strip()}')
        break
