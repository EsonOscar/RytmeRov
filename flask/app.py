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
from datetime import datetime, timezone
import psycopg2  # selv psycopg2 bibloiotket, til oprette forbindelse til db, kører sql kommandoer osv
import os
# gør man kan bruge row navn i steet for index i db
from psycopg2.extras import RealDictCursor
from test_graf import generate_ecg_graph
class ProxiedRequestHandler(WSGIRequestHandler):
    """Proxy request handler class, makes sure we can access the real client IP"""

    def address_string(self):
        # Split the X-Forwarded-For header and return the first
        # IP address
        forwarded = self.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return super().address_string()


# Initialise the flask app
app = Flask(
    __name__,
    static_folder="static",
    static_url_path="/home/3semprojekt/RytmeRov/flask/static",
)

# vi sætter en hemmelig nøgle som bare super
# hemmelig fordi adhd har skrevet det til
# session management og cookies
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

# Tell flask to trust the third entry in X-Forwarded-For
# The app is behind cloudflare, and a
# reverse proxy, so the third entry is the
# real client IP
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=2, x_proto=1)

# Create a login manager instance
login_manager = LoginManager()
# Set the login view for the login manager this is used to redirect users to the
# login page if they are not logged in
login_manager.login_view = "login"
# Initialize the login manager with the app
login_manager.init_app(app)


# Database connect
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
    print(
        "du er bare inde din flotte lille fæøreske eller svenske eller somaliske eller danske eller hvad du nu er "
    )
    return conn


# User class for Flask-Login


class User(UserMixin):
    """Current User class, extracts all necessary information about the current user from the database,
    and saves it to object attributes."""

    def __init__(self, row: dict):
        """row kommer ind fra db som en dictionary form som gør det mere læsbart og nemmere at arbejde med
        det er ved hjælp af RealDictCursor fra psycopg2 extras"""
        self.id = row["id"]  # her sætter vi alle vores properties til user klassen
        self.username = row["username"]
        self.password = row["password"]
        self.name = row["name"]
        self.lastname = row["lastname"]
        self.role = row["role"]
        # row.get er når man skal havde noget og none som default værdi hvis der ikke er noget data på last login 
        self.last_login = row.get("last_login", None)

    # vores to properties doktor og sysadmin bliver brugt til at tjekke om en bruger er doktor eller sysadmin
    @property
    # bruges til at tjekke om en bruger er admin derved returnere True og give adgang til sysadmin sider
    def sysadmin(self):
        return self.role == "sysadmin"

    @property
    # bruges til at tjekke om en bruger er doktor derved returere True dermed give adgang til doktor sider 
    def doctor(self):
        return self.role == "doctor"


# Load selected user from database

@login_manager.user_loader
def load_user(user_id):
    """ den her funktion loader en bruger fra databasen baseret på deres bruger id.
    den tager et bruger id som input og returnerer en User objekt hvis brugeren findes, ellers returnerer den None."""
    conn = db_connect()  # opretter forbindelse til db
    cur = conn.cursor()  # opretter en cursor til at eksekvere sql kommandoer
    try:
        # kommando for at hente brugere baseret på id 
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        # henter den første række fra resultatet af kommandoen og kommer ud i dictionary form
        row = cur.fetchone()
    except Exception as e:
        # hvis der kommer fejl i database fx forbindelse eller med kommando
        # og kører videre med at ved at sætte row til None
        print("fucking kæmpe fejl i load user funktionen din idiot", e)
        row = None  # hvis der er fejl sætter vi row til None, så kører vi videre
    finally:
        conn.close()  # lukker forbindelsen til db
    if row is None:
        return None  # hvis der ikke er nogen række fundet, returnerer vi None
    # hvis der er en række fundet, returnerer vi et user objekt med data
    return User(row)


# ############################################ WEBSITE ROUTES BELOW ############################################ #


# Index
# route
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


@app.route("/login", methods=["GET", "POST"])
# vores login route som håndtere både get og post requests GET viser login siden
# POST bliver brugt når brugeren sender login formen
def login():
    if current_user.is_authenticated:
        # hvis brugeren er logget ind allerede ind allerede bliver sendt til index
        return redirect(url_for("index"))

    if request.method == "GET":
        # hvis det er først gang de besøger login siden viser den login siden med get request
        return render_template("login.html")

    # request.form.get henter fra login formen, strip fjerner mellemrum før og efter 
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()

    if not username or not password:
        # hvis et af felterne er tomme og flasher en besked
        flash("udfyld nu fucking alle felter din idiot nu prøver vi igen", "warning")
        return redirect(url_for("login"))

    conn = db_connect()  # forbindelse til Databasen
    cur = conn.cursor()  # cursor til at sql kommandoer

    try:
        cur.execute(
            # sql kommandoet for at finde bruger i databasen baseret på username %S er en placeholder
            "select * FROM users Where username = %s",
            (username,),
        )
        # tager den række som matcher brugernavnet ud af databasen gemmer i dict form 
        row = cur.fetchone()

    except Exception as e:
        # hvis der er fejl i database forbindelse print fejl besked i terminal
        print(" der skete kæmpe fejl i DATABASEN uheldigt", e)
        conn.close()  # lukker forbindelsen til databasen
        # efter fejlen bliver beskeden flashet til brugeren 
        flash("der skete en fejl med databasen prøv igen senere.", "danger")
        # bliver så returet til start login siden
     
        return redirect(url_for("login"))

    if row is None:
        conn.close()
        flash(
            "den er ærgelig du forkert burgernavn eller password prøv lige igen din smukke mande mand eller kvnde kvinde",
            "danger",
        )
        # hvis tingene er forkerte send til login siden igen
        return redirect(url_for("login"))

    if not check_password_hash(row["password"], password):
        conn.close()
        flash(
            "den er ærgelig du forkert burgernavn eller password prøv lige igen din smukke mande mand eller kvnde kvinde",
            "danger",
        )
        # hvis tingene er forkerte send til login siden igen
        return redirect(url_for("login"))

    # her får vi nuværende tidspunkt som gør vi kan få og opdere last login feltet i datebasen
  
    now_iso = datetime.now(timezone.utc).isoformat()
    # det er i iso formmat som ser sådan her ud 2023-10-05T14:48:00+00:00
    try:
        cur.execute(
            # kører sql kommandoer som opdatere last login i databasen
            "UPDATE users set last_login = %s Where id = %s",
            # her sætter vi værdierne ind i placeholders 
            (now_iso, row["id"]),
        )
        conn.commit()  # gemmer ændringerne i databasen
    finally:
        conn.close()  # så lukker vi forbindelsen til databasen

    # laver et user objekt med data fra databasen
    user = User(row)
    # logger brugeren ind ved hjælp af flask login funktionen
    login_user(user)
    flash(f"hej {user.name}, du er nu logget ind dine heldig bandit.", "success")
    # efter man logger man logger ind bliver du ført til index
    return redirect(url_for("index"))


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash(
        "You have been logged out fucking moron bonus info oscar lugter af marmelade burger.", "info"
    )
    return redirect(url_for("index"))



@app.route("/sysadmin")
@login_required
def sysadmin():
    if not current_user.sysadmin: # her tjekker vi om brugeren er sysadmin
        # Forbidden
        abort(403)
    return render_template("sysadmin.html")

@app.route ("/create_user", methods=["GET", "POST"])
@login_required
def create_user():
    if not current_user.sysadmin:
        abort (403)
    
    if request.method == "GET":
        return render_template ("create_user.html")
    # behnandler post request herunder
    username = request.form.get ("username", "").strip()
    password = request.form.get ("password", "").strip()
    name = request.form.get ("name", "").strip()
    lastname = request.form.get ("lastname", "").strip()
    role = request.form.get ("role", "").strip()

    # her sikre vi alle felter er udfyldt som champs
    if not username or not password or not name or not lastname or not role: 
        flash ("vil de være så venlig at udfylde alle felter tak din smukke person", "warning")
        return redirect (url_for ("create_user"))
    if role not in ["sysadmin", "doctor"]:
        flash ("rollen skal være sysadmin eller doctor tak" , "warning")
        return redirect (url_for ("create_user"))
    
    #vi skal sku da også havde hastet passwordet før vi connecter til vores db bro
    hashed_password = generate_password_hash(password) # hasher passwordet så det ikke er i plain text i db
    now_iso = datetime.now(timezone.utc).isoformat() # giver den lige nuværende tidspunkt i iso format

    conn = db_connect()
    cur = conn.cursor() 

    try: 
        cur.execute ( 
            """
            INSERT INTO users (username, password, name, lastname, role, created, last_login) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            ,
            (username, hashed_password, name, lastname, role, now_iso, now_iso) # sætter værdierne ind i placeholders  
         )
        conn.commit() # gemmer nye bruger i db
        flash (f"bruger {username} er nu oprettet succesfuldt din fantastiske person", "success")
        return redirect (url_for ("index"))
    
    except psycopg2.Error as e: # psycopg2 fejl håndtering for postgres specifikke fejl
        print ("fejl ved oprettelse af bruger i db", e)
        flash ("der skete en fejl prøv igen", "danger")
        return redirect (url_for ("create_user"))
    
    finally:
        conn.close() # lukker forbindelsen til db

@app.route("/bruger_administration")
@login_required
def bruger_administration():
    if not current_user.sysadmin:
        abort (403)
    
    conn = db_connect()
    cur = conn.cursor()

    try:
        cur.execute (
            """
            SELECT id, username, name, lastname, role, created, last_login 
            FROM users
            ORDER BY id """
        )

        users = cur.fetchall () # her henter vi alle brugere fra databasen som en liste af dictionaries
    finally: 
        conn.close()    
    
    return render_template ("bruger_administration.html", users=users) # sender brugerne afsted til template 

@app.route("/delete_user/<int:user_id>", methods=["POST"])
@login_required
def delete_user(user_id): 
    if not current_user.sysadmin:
        abort (403)

    if current_user.id == user_id:
        flash ("du må ikke slette dig selv dont do it be that guy", "warning")
        return redirect (url_for ("bruger_administration"))
    
    conn= db_connect()
    cur = conn.cursor()

    try: #vi tjekker self lige først om brugeren eksistere før vi overhovedet kan slette den 
        cur.execute ("""SELECT id, username, deleted_at  
        FROM users WHERE id = %s
        """, (user_id, )),
        user = cur.fetchone()

        if user is None: # tjekker om brugeren findes 
            flash ("brugeren er allerede slettet eller eksistere ikke mere", "warning")
            return redirect (url_for ("bruger_administration"))
        # hvis den findes så sletter vi den (evil laugh)
        cur.execute ("delete FROM users WHERE id = %s", (user_id,))
        conn.commit()
        flash(f"så er brugeren '{user['username']}' er nu slettet forevigt")
        return redirect(url_for("bruger_administration"))

    except psycopg2.Error as e:
        print("fejl angånde sletningen af brugeren skete i databasen")
        flash("der skete en fejl")
        return redirect(url_for("bruger_administration"))
    finally:
        conn.close()




@app.route("/dashboard")
@login_required
def dashboard():
    print(current_user.role)
    if current_user.role == "sysadmin": # her tjekker vi om brugeren er sysadmin hvis ikke kommer ud ikke ind du 
        return render_template("dashboard.html")
    elif current_user.role == "doctor":
        graf_data = generate_ecg_graph()
        return render_template("dashboard_doctor.html",data=graf_data)
    else:
        # Forbidden
        abort(403)



# ################################################# API #################################################### #

@app.route("/api/data_test", methods=["POST"])
def data_test():
    print("\nESP32 Connection: data_test API endpoint hit")
    data = request.get_data(as_text=True)
    if data:
        #print(data, "\n")
        #data = data.strip().split("\n")
        
        #for i in range(len(data)):
           # data[i] = data[i].split(",")
        print("Data recieved!")
        #print(data, "\n")
            
        key = os.getenv("ENC_KEY")
        fer = Fernet(key.encode())
        if not key:
            print("Error loading encryption key from environment, redirecting...")
            return (jsonify({"Success": False}))
        else:
            print("Encryption key successfully loaded!")
            
        cpr = data.strip().split("\n")[0]
        print(cpr)
        
        try:
            conn = db_connect()
            cur = conn.cursor()
            
            cur.execute("""
                        SELECT cpr_hash FROM patients
                        """)
            db_cpr = cur.fetchall()
            
            if len(db_cpr) != 0:
                for i in range(len(db_cpr)):
                    check = check_password_hash(db_cpr[i], cpr)
                    if check == True:
                        break
                    else:
                        pass
            else:
                check = False
                    
            print(check)
            print(db_cpr)
            
            if not check:
                enc_cpr = fer.encrypt(cpr.encode()).decode()
                cpr_hash = generate_password_hash(cpr)
                #print(enc_cpr, "\n", cpr_hash)
                cur.execute(
                    """
                    INSERT INTO patients (cpr, cpr_hash) VALUES (%s, %s)
                    """, (enc_cpr, cpr_hash)
                )
                conn.commit()
                print("New data inserted into DB.")
            
            
        except Exception as e:
            print(f"Error: {e}")
        finally:
            cur.close()
            conn.close()
        
        cpr = None
        
        file_name = Fernet.generate_key().decode()[:-1]
        
        enc_data = fer.encrypt(data.encode())
        #print(enc_data)
        with open(f"ecg/{file_name}.csv", "w") as f:
            f.write(str(enc_data.decode()))
        
        with open("recv_data.csv", "w") as f:
            f.write(str(data))
        return (jsonify({"Success": True}), 200)
    else:
        return (jsonify({"Success": False}))

# ################################################## CONFIG #################################################### #
"""
 This is only used when running the app locally,
 gunicorn is used in production and ignores this. 
 Config, app runs locally on port 8000. 
 NGINX proxies outisde requests to this port, and sends th eapps response back to the client.
 """
if __name__ == "__main__":
    app.run(debug=True, port=8000)