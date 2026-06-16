import pymysql, json
config = json.load(open('config.json'))
conn = pymysql.connect(host=config['db_host'], port=config['db_port'], user=config['db_user'], password=config['db_pass'], db=config['db_name'], cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
tables = ['lab_samples', 'lab_tests', 'invoices', 'lis_collection_points', 'patients', 'patient_consents', 'lis_ddt']
for table in tables:
    try:
        cur.execute("SHOW COLUMNS FROM `%s`" % table)
        cols = cur.fetchall()
        for c in cols:
            if 'username' in c['Field'].lower():
                print("Table: %s -> FIELD: %s | Null:%s | Default:%s | Extra:%s" % (table, c['Field'], c['Null'], c['Default'], c['Extra']))
    except Exception as e:
        print("Table %s: ERROR %s" % (table, e))
conn.close()
