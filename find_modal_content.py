import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

modal_ids = ['modal-enter-results', 'modal-lis-reporting-detail', 'modal-lis-report-view']

for mid in modal_ids:
    print("="*80)
    print(f"MODAL: {mid}")
    print("="*80)
    # Find the div matching id="mid" and trace its content until the matching closing div
    start_match = re.search(r'<div\s+[^>]*id=["\']' + mid + r'["\'][^>]*>', content)
    if start_match:
        start_pos = start_match.start()
        # Find closing div of this modal
        div_count = 1
        pos = start_match.end()
        while div_count > 0 and pos < len(content):
            if content[pos:pos+4] == '<div':
                div_count += 1
                pos += 4
            elif content[pos:pos+5] == '</div':
                div_count -= 1
                pos += 5
            else:
                pos += 1
        # Print first 1000 characters of the modal
        modal_html = content[start_pos:pos]
        print(modal_html[:1500] + "\n... (truncated) ...\n" if len(modal_html) > 1500 else modal_html)
    else:
        print("Not found")
