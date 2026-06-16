path = r"C:\Users\robpiron\.gemini\antigravity\brain\b6a0698d-44d4-4051-93fe-d78e80182f55\scratch\append_remaining_code.py"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"Total length of file: {len(content)}")
print("=== FIRST 1000 CHARS ===")
print(content[:1000])
print("\n=== LAST 1000 CHARS ===")
print(content[-1000:])
