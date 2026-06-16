with open('schema.sql', 'r', encoding='utf-8') as f:
    content = f.read()

import re
# Match table names in CREATE TABLE
matches = re.findall(r'CREATE TABLE\s+(?:IF NOT EXISTS\s+)?`?([a-zA-Z_0-9]+)`?', content, re.IGNORECASE)
print("Tables in schema.sql:")
print(matches)
