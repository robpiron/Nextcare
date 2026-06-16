with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

start = html.find('<section id="tab-hris"')
end = html.find('<!-- 10. ACCOUNTING & INVOICING TAB -->')
if start != -1 and end != -1:
    print(html[start:start+1500])
    print("...")
    print(html[end-800:end])
else:
    print("Not found")
