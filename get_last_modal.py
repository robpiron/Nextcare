with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="modal-worksheet-title"')
if idx != -1:
    # Print the modal structure and check where it ends
    # We want to find the closing tag of this modal
    pos = html.find('</div>', idx)
    # let's print 500 chars before and 800 chars after
    print(html[idx - 100:idx + 1000])
else:
    print("Not found")
