with open('schema.sql', 'r', encoding='utf-8') as f:
    content = f.read()

import re
tables = re.findall(r'CREATE TABLE `?([a-zA-Z_0-9]+)`?', content, re.IGNORECASE)
print("Tables in schema.sql:")
print(tables)
