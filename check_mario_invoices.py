import pymysql, json
config = json.load(open('config.json'))
conn = pymysql.connect(host=config['db_host'], port=config['db_port'], user=config['db_user'], password=config['db_pass'], db=config['db_name'], cursorclass=pymysql.cursors.DictCursor)
cur = conn.cursor()
pid = 1
cur.execute("""
    SELECT DISTINCT i.id, i.invoice_number, i.amount_due, i.payment_status, i.issue_date
    FROM invoices i
    LEFT JOIN admissions adm ON i.admission_id = adm.id
    LEFT JOIN appointments app ON i.appointment_id = app.id
    LEFT JOIN lab_samples ls ON i.sample_id = ls.id
    LEFT JOIN radiology_studies rs ON i.study_id = rs.id
    WHERE adm.patient_id = %s OR app.patient_id = %s OR ls.patient_id = %s OR rs.patient_id = %s
    ORDER BY i.issue_date DESC
""", (pid, pid, pid, pid))
rows = cur.fetchall()
print("Trovate %d fatture per Mario Rossi:" % len(rows))
for r in rows:
    print("  #%s | euro%.2f | %s | %s" % (r['invoice_number'], float(r['amount_due']), r['payment_status'], r['issue_date']))
conn.close()
