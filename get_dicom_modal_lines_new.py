with open('index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for idx, line in enumerate(lines):
    if 'id="modal-dicom-viewer"' in line:
        print(f"Start: {idx + 1}")
        for j in range(idx, idx + 150):
            if 'modal-add-admission' in lines[j]:
                print(f"End: {j}")
                break
        break
