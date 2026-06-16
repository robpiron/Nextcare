with open('portal_template.html', 'r', encoding='utf-8') as f:
    content = f.read()

import re
matches = [m.start() for m in re.finditer(r'</script>', content)]
print("Script tags close at chars:", matches)
# Let's print the 200 characters before the last </script>
if matches:
    last_close = matches[-1]
    print(content[last_close-300:last_close])
