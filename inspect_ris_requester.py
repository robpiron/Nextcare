with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="modal-add-ris"')
if idx != -1:
    # Print the markup from the start of the modal down to the service selection
    print(html[idx:idx+2500])
