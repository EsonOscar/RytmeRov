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
    
    cur.execute("TRUNCATE TABLE ekg")
    conn.commit()
    cur.execute("TRUNCAtE TABLE patients")
    conn.commit()
except Exception as e:
    print(f"Error when trunatin tables. Error {e}")