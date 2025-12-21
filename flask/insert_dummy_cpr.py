from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.serving import WSGIRequestHandler
from cryptography.fernet import Fernet
from datetime import datetime, timezone
import jwt
import psycopg2  # selv psycopg2 bibloiotket, til oprette forbindelse til db, kører sql kommandoer osv
import hashlib # This and hmac is for generating deterministic hashes, for saving CPRs
import hmac
import os
import ecg
# gør man kan bruge row navn i steet for index i db
from psycopg2.extras import RealDictCursor
from test_graf import generate_ecg_graph
import app

conn = app.db_connect()
cur = conn.cursor()

cpr = "1111111111"
print(cpr)

key = os.getenv("ENC_KEY")
fer = Fernet(key.encode())

pepper = os.environ.get("CPR_PEPPER")
enc_cpr = fer.encrypt(cpr.encode()).decode()
# Deterministic hashing
cpr_hash = hmac.new(pepper.encode(), cpr.encode(), hashlib.sha256).hexdigest()
print(cpr_hash)

cur.execute("""
            INSERT INTO patients (cpr, cpr_hash) VALUES (%s, %s)
            """,
            (enc_cpr, cpr_hash))

conn.commit()

