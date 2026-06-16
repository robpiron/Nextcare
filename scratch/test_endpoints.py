import urllib.request
import json
import pymysql

# Load config
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

# Helper for POST requests
def post_api(endpoint, payload):
    url = f"http://127.0.0.1:8000{endpoint}"
    req_data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except urllib.error.HTTPError as he:
        print(f"HTTP Error for {endpoint}: {he.code}")
        print(he.read().decode('utf-8'))
        return {"success": False, "error": he.reason}
    except Exception as e:
        print(f"Error connecting to {endpoint}: {e}")
        return {"success": False, "error": str(e)}

def run_tests():
    # 1. Test Login Collection Point
    print("\n--- Testing Collection Point Login ---")
    login_res = post_api('/api/portals-login', {
        "username": "ostia",
        "password": "ostia",
        "portal_type": "collection_point",
        "cp_code": "PP-OSTIA"
    })
    print("CP Login Result:", login_res)
    assert login_res.get("success"), "CP Login failed"
    
    # 2. Test CP Data retrieval
    print("\n--- Testing CP Data Retrieval ---")
    cp_data = post_api('/api/portal-cp-data', {
        "collection_point_id": 1 # PP-OSTIA is ID 1 in seeds
    })
    print("CP Data Keys:", cp_data.get("data", {}).keys() if cp_data.get("success") else "FAILED")
    assert cp_data.get("success"), "CP Data retrieval failed"
    
    # 3. Test Company Login
    print("\n--- Testing Company Login ---")
    comp_login = post_api('/api/portals-login', {
        "username": "acme",
        "password": "123",
        "portal_type": "company"
    })
    print("Company Login Result:", comp_login)
    assert comp_login.get("success"), "Company Login failed"
    
    # 4. Test Company Data retrieval
    print("\n--- Testing Company Data Retrieval ---")
    comp_data = post_api('/api/portal-company-data', {
        "company_id": 1 # Acme Corp is ID 1
    })
    print("Company Data Keys:", comp_data.get("data", {}).keys() if comp_data.get("success") else "FAILED")
    assert comp_data.get("success"), "Company Data retrieval failed"
    
    # 5. Test Upsert
    print("\n--- Testing Upsert Records ---")
    conn = pymysql.connect(
        host=config.get('db_host', 'localhost'),
        port=int(config.get('db_port', 3306)),
        user=config.get('db_user', 'root'),
        password=config.get('db_pass', ''),
        database=config.get('db_name', 'nextcare_db'),
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM patients")
    before_count = cursor.fetchone()[0]
    
    # Insert a new patient via upsert
    upsert_res = post_api('/api/portal-upsert-records', {
        "table_name": "patients",
        "rows": [{
            "id": 99999,
            "uuid": "p-test-99999",
            "last_name": "TestUpsert",
            "first_name": "User",
            "tax_code": "TSTUSR99X99X999X",
            "birth_date": "1999-09-09",
            "gender": "M"
        }]
    })
    print("Upsert Result:", upsert_res)
    assert upsert_res.get("success"), "Upsert failed"
    
    cursor.execute("SELECT COUNT(*) FROM patients")
    after_count = cursor.fetchone()[0]
    print(f"Patients count before: {before_count}, after: {after_count}")
    
    # Clean up test patient
    cursor.execute("DELETE FROM patients WHERE id = 99999")
    conn.commit()
    conn.close()
    
    print("\n=======================================================")
    print("ALL API ENDPOINTS TESTED AND VALIDATED SUCCESSFULLY!")
    print("=======================================================")

if __name__ == "__main__":
    run_tests()
