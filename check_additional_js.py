with open('additional_js_code.js', 'r', encoding='utf-8') as f:
    lines = [f.readline() for _ in range(50)]

for idx, line in enumerate(lines, 1):
    print(f"{idx}: {line.strip()}")
