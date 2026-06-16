import re

with open('app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# Check for uninitialized consts
# e.g., const name;
uninit_const = re.findall(r'const\s+[a-zA-Z0-9_]+\s*;', code)
print(f"Uninitialized const declarations: {uninit_const}")

# Check for duplicate function declarations
funcs = re.findall(r'function\s+([a-zA-Z0-9_]+)\s*\(', code)
duplicates = set([x for x in funcs if funcs.count(x) > 1])
print(f"Duplicate function declarations: {duplicates}")

# Check for window.func duplicate assignments
window_funcs = re.findall(r'window\.([a-zA-Z0-9_]+)\s*=', code)
win_duplicates = set([x for x in window_funcs if window_funcs.count(x) > 1])
print(f"Duplicate window function assignments: {win_duplicates}")

# Let's inspect the duplicate window functions
if win_duplicates:
    print("\nDuplicate window functions details:")
    for wd in win_duplicates:
        matches = [m.start() for m in re.finditer(r'window\.' + re.escape(wd) + r'\s*=', code)]
        print(f"- {wd}: {len(matches)} times")
        for m in matches:
            # print line number
            line_num = code[:m].count('\n') + 1
            print(f"  Line {line_num}")
