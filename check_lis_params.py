import pymysql, json
config = json.load(open('config.json'))
conn = pymysql.connect(host=config['db_host'], port=config['db_port'], user=config['db_user'], password=config['db_pass'], db=config['db_name'], cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()

# Check LIS services and their parameters JSON structure
cur.execute("SELECT id, name, type, parameters FROM medical_services WHERE type = 'lis' LIMIT 5")
rows = cur.fetchall()
print("=== Sample LIS services with parameters ===")
for r in rows:
    params = json.loads(r['parameters']) if r['parameters'] else []
    print("Service: %s (id=%s)" % (r['name'], r['id']))
    if params:
        print("  Param count:", len(params))
        print("  First param keys:", list(params[0].keys()) if params else 'none')
        print("  First param:", json.dumps(params[0], ensure_ascii=False, indent=2)[:500])
    else:
        print("  No parameters")
    print()

# Also check whats_new / news table
cur.execute("SHOW TABLES LIKE '%news%'")
news_tables = cur.fetchall()
print("News tables:", news_tables)

cur.execute("SHOW TABLES LIKE '%update%'")
upd_tables = cur.fetchall()
print("Update tables:", upd_tables)

# Check lab_tests with full structure
cur.execute("SELECT * FROM lab_tests LIMIT 2")
tests = cur.fetchall()
print("\n=== Sample lab_tests ===")
for t in tests:
    print(t)

conn.close()
