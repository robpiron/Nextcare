with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

idx = html.find('id="tab-fse-transmissions"')
if idx != -1:
    # Find table inside this section
    table_idx = html.find('<table', idx)
    if table_idx != -1:
        print(html[table_idx:table_idx+1500])
