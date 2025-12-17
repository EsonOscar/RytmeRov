import os
import psycopg2
from psycopg2.extras import RealDictCursor

def db_connect():
    """ her opretter vi forbindelse til den flotte prosgres database
    de værdier kommer fra miljø variablerne, så password og brugernavn ikke er hardcoded i koden"""
    conn = psycopg2.connect(
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT"),
        cursor_factory=RealDictCursor, 
    )

    
    return conn
       
   


if __name__ == "__main__":
    try:
        conn = db_connect()
        cur = conn.cursor()

        print("\n✅ Connection successful!\n")

        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)

        tables = cur.fetchall()
        print("📌 Dine Postgres tabeller:\n")
        for t in tables:
            print(" -", t["table_name"])

        conn.close()

    except Exception as e:
        print("\n❌ Connection FAILED!\n")
        print("Error:", e)
    print("du er fucking inde din mægso")