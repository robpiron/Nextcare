with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in app.js: {len(lines)}")
print("=== LAST 100 LINES OF app.js ===")
for idx, line in enumerate(lines[-100:], len(lines) - 99):
    print(f"{idx}: {line.strip()}")
