import psycopg2
import sys
import os


folder_path = '/home/3semprojekt/RytmeRov/flask/ecg'

print(f"Deleting all files in {folder_path}...")

for filename in os.listdir(folder_path):
    #print(filename)
    file_path = os.path.join(folder_path, filename)
    if os.path.isfile(file_path):
        if file_path == "/home/3semprojekt/RytmeRov/flask/ecg/clear_folder.py":
            pass
        else:
            os.remove(file_path)
        
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
    
    print("Truncating the EKG table...")
    cur.execute("TRUNCATE TABLE ekg")
    conn.commit()
    print("Table successfully truncated.")
    
except Exception as e:
    print(f"Error when truncating the EKG table: {e}")
    
finally:
    cur.close()
    conn.close()
    
print("Program done\n")