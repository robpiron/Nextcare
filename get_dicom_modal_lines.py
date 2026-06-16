with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx in range(4930, 5067):
    print(f"{idx+1}: {lines[idx].rstrip()}")
