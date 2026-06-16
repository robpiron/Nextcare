import re

with open('schema.sql', 'r', encoding='utf-8') as f:
    schema = f.read()

create_tables = re.findall(r'CREATE TABLE IF NOT EXISTS `(\w+)`|CREATE TABLE `(\w+)`', schema, re.IGNORECASE)
tables = [t[0] or t[1] for t in create_tables]
print("Tables in schema.sql:")
for t in tables:
    print(f"  {t}")
