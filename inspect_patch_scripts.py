import os

scratch_dir = r"C:\Users\robpiron\.gemini\antigravity\brain\b6a0698d-44d4-4051-93fe-d78e80182f55\scratch"

patches = [
    'patch_app_js_part1.py', 'patch_app_js_part2.py', 'patch_app_js_part3.py',
    'patch_app_js_part4.py', 'patch_app_js_all.py'
]

for patch in patches:
    path = os.path.join(scratch_dir, patch)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"\n=== PATCH {patch} (size: {len(content)}) ===")
        print("First 800 chars:")
        print(content[:800])
        print("..." if len(content) > 800 else "")
    else:
        print(f"Patch {patch} not found at {path}")
