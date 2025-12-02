from flask import (
    Flask,
    session,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    jsonify,
    abort,
    send_from_directory,
)
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.serving import WSGIRequestHandler
from cryptography.fernet import Fernet
import psycopg2 #selv psycopg2 bibloiotket, til oprette forbindelse til db, kører sql kommandoer osv
import os 
from psycopg2.extras import RealDictCursor #gør man kan bruge row navn i steet for index i db




class ProxiedRequestHandler(WSGIRequestHandler):
    """Proxy request handler class, makes sure we can access the real client IP"""

    def address_string(self):
        # Split the X-Forwarded-For header and return the first IP address
        forwarded = self.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return super().address_string()

# Initialise the flask app
app = Flask(
    __name__,
    static_folder="static",
    static_url_path="",
    )

# Tell flask to trust the third entry in X-Forwarded-For
# The app is behind cloudflare, and a reverse proxy, so the third entry is the real client IP
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=1)

# Create a login manager instance
login_manager = LoginManager()
# Set the login view for the login manager
# this is used to redirect users to the login page if they are not logged in
login_manager.login_view = "login"
# Initialize the login manager with the app
login_manager.init_app(app)

#Database connect 
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



# User class for Flask-Login
class User(UserMixin):
    """Current User class, extracts all necessary information about the current user from the database,
    and saves it to object attributes."""

    def __init__(self, row):
        
        #REWRITE ALL OF THIS
        
        self.id = row["id"]
        self.username = row["username"]
        self.password = row["password"]
        self.name = row["name"]
        self.lastname = row["lastname"]
        self.email = row["email"]
        self.role = row["role"]
        self.accepted_terms_at = row["accepted_terms_at"]
    
# Load selected user from database
# REWRITE THIS
@login_manager.user_loader
def load_user(user_id):
    conn = db_connect()
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return User(row) if row else None

# ############################################ WEBSITE ROUTES BELOW ############################################ #

#Index route
@app.route("/")
@app.route("/index")
@app.route("/home")
def index():
    return render_template("index.html")

@app.route("/min_profil")
def min_profil():
    return render_template("min_profil.html")   

@app.route("/kontakt")
def kontakt():
    return render_template("kontakt.html")

@app.route("/teamet")
def teamet():
    return render_template("teamet.html")

@app.route("/Mere_om_RytmeRov")
def mere_om_rytmerov():
    return render_template("mere_om_rytmerov.html")

@app.route("/login.html")
def login():
    return render_template("login.html")

@app.route("/logout")
@login_required 
def logout():
    logout_user()
    flash("You have been logged out fucking moron bonus info oscar lugter af marmelade burger.", "info")
    return redirect(url_for("index"))

@app.route("/admin")
@login_required
def admin():
    if current_user.role != "admin":
        abort(403)  # Forbidden
    return render_template("admin.html")






# ################################################## CONFIG #################################################### #

# This is only used when running the app locally,
# gunicorn is used in production and ignores this.

# Config, app runs locally on port 8000.
# NGINX proxies outisde requests to this port,
# and sends the apps response back to the client.
if __name__ == "__main__":
    app.run(
        debug=True, port=8000, host="127.0.0.1", request_handler=ProxiedRequestHandler
    )
