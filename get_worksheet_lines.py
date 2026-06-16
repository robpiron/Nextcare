with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="modal-add-worksheet"' in line:
        for j in range(idx - 2, idx + 10):
            print(f'{j+1}: {lines[j].strip()}')
        break

for idx, line in enumerate(lines):
    if 'id="requester-doctors-list"' in line:
        for j in range(idx - 10, idx + 5):
            print(f'{j+1}: {lines[j].strip()}')
        break
