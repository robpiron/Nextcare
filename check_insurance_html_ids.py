with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

def check_exist(name):
    if name in html:
        print(f"'{name}' exists in index.html")
    else:
        print(f"'{name}' is MISSING from index.html")

check_exist('config-insurances-table')
check_exist('config-select-listino')
check_exist('config-prices-table')
check_exist('config-tubes-table')
