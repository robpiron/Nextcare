with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find('id="modal-add-ris"')
if idx != -1:
    modal_content = content[idx:idx+5000]
    import re
    # find all id="..." inside the modal content
    ids = re.findall(r'id="([^"]+)"', modal_content)
    print("IDs in modal-add-ris:")
    print(ids)
