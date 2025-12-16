from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
from cryptography.fernet import Fernet
import psycopg2
import hashlib
import hmac
import os

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

key = os.environ.get("ENC_KEY")
fer = Fernet(key.encode())

test_cpr = "9309064435"

pepper = os.environ.get("CPR_PEPPER")
test_hash = hmac.new(pepper.encode(), test_cpr.encode(), hashlib.sha256).hexdigest()

try:
    conn = psycopg2.connect(
        user=db_user,
        password=db_pass,
        port=db_port,
        database=db_name
    )
    
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM patients WHERE cpr_hash = %s", (test_hash,))
    pat_id = cur.fetchone()[0]
    
    print(pat_id)
    
    cur.execute("SELECT ekg FROM ekg WHERE patient_id = %s ORDER BY timestamp DESC", (pat_id,))
    enc_ecg_files = cur.fetchall()
    newest_ecg = f"{enc_ecg_files[0][0]}.csv"
        
    
    print(enc_ecg_files)
    print(newest_ecg)
    
    with open(f"/home/3semprojekt/RytmeRov/flask/ecg/{newest_ecg}", "r") as f:
        enc_ecg = f.read()
    
    ecg = fer.decrypt(enc_ecg.encode()).decode().strip().split("\n")
    
    for i in range(5):
        print(ecg[i])
    print("...")
    

except Exception as e:
    print(f"Error: {e}")

finally:
    cur.close()
    conn.close()