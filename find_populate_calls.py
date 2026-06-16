with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in [12190, 12564]:
    if idx < len(lines):
        for j in range(idx - 5, idx + 10):
            print(f'{j+1}: {lines[j].strip()}')
        print("-" * 30)
