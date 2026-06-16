with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re
match = re.search(r'<div[^>]*?id="modal-dicom-viewer".*?<!--\s*End\s*modal\s*-->', html, re.DOTALL | re.IGNORECASE)
if match:
    print(match.group(0)[:1500])
else:
    # Try just searching for modal-dicom-viewer
    idx = html.find('modal-dicom-viewer')
    if idx != -1:
        print(html[idx:idx+1500])
    else:
        print("modal-dicom-viewer NOT found in index.html")
