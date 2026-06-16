import os
import json
import pymysql

def regenerate():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(base_dir, "config.json")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    conn = pymysql.connect(
        host=config.get('db_host', 'localhost'),
        port=int(config.get('db_port', 3306)),
        user=config.get('db_user', 'root'),
        password=config.get('db_pass', ''),
        database=config.get('db_name', 'nextcare_db'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM `lis_collection_points`")
    cp_rows = cursor.fetchall()
    conn.close()

    template_path = os.path.join(base_dir, "portal_template.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    for cp_row in cp_rows:
        cp_code = cp_row['code']
        portal_filename = f"portal_{cp_code}.html"
        portal_path = os.path.join(base_dir, portal_filename)
        
        html_content = html_template.replace("__CP_CODE__", cp_code)
        html_content = html_content.replace("__CP_NAME__", cp_row.get('name', 'Punto Prelievo'))
        html_content = html_content.replace("__CP_ID__", str(cp_row.get('id', 0)))
        
        with open(portal_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"Regenerated {portal_filename} successfully!")

if __name__ == "__main__":
    regenerate()
