import re

with open('app.js', 'r', encoding='utf-8') as f:
    content = f.read()

start_match = re.search(r'audit_logs:\s*\[', content)
if start_match:
    start_idx = start_match.end() - 1
    brace_count = 1
    end_idx = start_idx + 1
    while brace_count > 0 and end_idx < len(content):
        char = content[end_idx]
        if char == '[':
            brace_count += 1
        elif char == ']':
            brace_count -= 1
        end_idx += 1
    print(content[start_idx:end_idx])
else:
    print("audit_logs not found")
