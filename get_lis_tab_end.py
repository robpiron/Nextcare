with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

found_tab_lis = False
for idx, line in enumerate(lines):
    if 'id="tab-lis"' in line:
        found_tab_lis = True
    if found_tab_lis and idx > 800:
        if 'id="tab-ris"' in line:
            print(f"Start of tab-ris: {idx + 1}")
            for j in range(idx - 10, idx + 5):
                print(f"{j+1}: {lines[j].strip()}")
            break
