with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<section id="tab-hris"')
if start != -1:
    # Find matching closing section tag
    count = 0
    pos = start
    while pos < len(html):
        sec_start = html.find('<section', pos)
        sec_end = html.find('</section>', pos)
        if sec_end == -1:
            break
        if sec_start != -1 and sec_start < sec_end:
            count += 1
            pos = sec_start + 8
        else:
            count -= 1
            if count == 0:
                print(html[start:sec_end + 10])
                break
            pos = sec_end + 10
else:
    print("Not found")
