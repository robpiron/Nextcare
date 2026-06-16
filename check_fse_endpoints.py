with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

funcs = ['handle_fse_transmissions_list', 'handle_fse_cda_preview', 'handle_fse_manual_send']
for func in funcs:
    idx = content.find(f'def {func}')
    if idx != -1:
        print(f"=== {func} ===")
        print(content[idx:idx+1500])
        print("=" * 60)
    else:
        print(f"{func} NOT found")
