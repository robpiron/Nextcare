with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

lines = code.split('\n')
print("Occurrences of initialization function calls:")
for idx, line in enumerate(lines, 1):
    if 'initNavigation(' in line or 'DOMContentLoaded' in line or 'window.onload' in line or 'initTheme(' in line:
        # print line and 5 surrounding lines
        print(f"\nLine {idx}:")
        start = max(0, idx - 5)
        end = min(len(lines), idx + 5)
        for i in range(start, end):
            prefix = ">>>" if i + 1 == idx else "   "
            print(f"{prefix} {i+1}: {lines[i]}")
