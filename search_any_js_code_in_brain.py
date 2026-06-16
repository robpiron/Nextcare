import os

brain_dir = r"C:\Users\robpiron\.gemini\antigravity\brain\b6a0698d-44d4-4051-93fe-d78e80182f55"
target = 'renderSsnRecipes'

matches = []
for root, dirs, files in os.walk(brain_dir):
    for f in files:
        if f.endswith(('.py', '.md', '.txt', '.js')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file_obj:
                    if target in file_obj.read():
                        matches.append(path)
            except Exception:
                pass

print("Found target in files:")
for m in matches:
    print(m)
