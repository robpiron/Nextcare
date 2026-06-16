with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

funcs = [
    'handle_compensations_config_save', 'handle_compensations_list', 
    'handle_compensations_config_delete', 'handle_compensations_payout'
]

for func in funcs:
    idx = content.find(f'def {func}')
    if idx != -1:
        print(f"=== METHOD {func} ===")
        print(content[idx:idx+1500])
        print("="*60)
    else:
        print(f"Method {func} NOT found")
