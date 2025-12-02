from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone, timedelta
import psycopg2
import os

db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_port = os.environ.get("DB_PORT")
db_name = os.environ.get("DB_NAME")

password = generate_password_hash(db_pass)

try:
    conn = psycopg2.connect(
        user=db_user,
        password=db_pass,
        port=db_port,
        database=db_name
    )
    
    cur = conn.cursor()
    
    print("\nConnection successful!\n")
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cur.fetchall()
    print(tables, "\n")
    #print(conn.get_dsn_parameters(), "\n")
    
    timestamp = f"{datetime.now(timezone.utc)}"[:-13]
    #print(timestamp)
    
    """
    cur.execute("INSERT INTO users 
                (username, password, name, lastname, role, created, last_login) 
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s)",
                ("SysAdmin", password, "Sysadmin", "", "sysadmin", timestamp, timestamp))
    """
    #conn.commit()
    #print("Initial SysAdmin user seeded in DB")
    
    cur.execute("SELECT * FROM users")
    res = cur.fetchall()
    print(res)
    
    
    conn.close()
    
except Exception as e:
    print(f"Error din lille idiot:\n{e}")