with open('app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print("=== renderReportingServices ===")
for idx in range(16164, 16225):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
print("\n=== renderReportingAcceptances ===")
for idx in range(16598, 16660):
    if idx < len(lines):
        print(f"{idx+1}: {lines[idx].strip()}")
