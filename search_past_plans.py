with open(r"C:\Users\robpiron\.gemini\antigravity\brain\b6a0698d-44d4-4051-93fe-d78e80182f55\past_implementation_plans.md", 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer('renderSsnRecipes', content)]
print(f"Found 'renderSsnRecipes' {len(matches)} times")
for m in matches:
    print(content[max(0, m-200):m+500])
    print("=" * 60)
