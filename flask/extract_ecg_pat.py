from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
import psycopg2
import os

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

try:
    conn = psycopg2.connect(
        user=db_user,
        password=db_pass,
        port=db_port,
        database=db_name
    )
    
    cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM patients")
        pat = cur.fetchall()
    except Exception as e:
        print(f"Error getting patient data. Error: {e}")
        
    try:
        cur.execute("SELECT * FROM ekg")
        ecg = cur.fetchall()
    except Exception as e:
        print(f"Error getting ECG data. Error: {e}")
    
    print("===========================================================")
    print("PATIENTS:")
    for i in range(len(pat)):
        print("\n")
        print(f"Entry {i}:")
        for elem in pat[i]:
            print(f"Data: {elem}")
    print("===========================================================")
    print("ECG:")
    for i in range(len(ecg)):
        print("\n")
        print(f"Entry {i}:")
        for elem in ecg[i]:
            print(f"Data: {elem}")
    print("===========================================================")
except Exception as e:
    print(f"Error loading DB data. Error: {e}")
    
time = str(datetime.now(timezone.utc))
print(f"\nTime: {time[:-13]}")