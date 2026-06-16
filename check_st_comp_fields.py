with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="modal-add-staff"')
if idx != -1:
    snippet = html[idx:idx+6500]
    comp_idx = snippet.find('Regola Compenso di Default')
    if comp_idx != -1:
        print("HTML snippet around compensation rule:")
        print(snippet[comp_idx-100:comp_idx+2200])
