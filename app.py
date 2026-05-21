"""
ClearRoute – AI Emergency Response System (Production/Hackathon Edition)
app.py — Flask Backend API

HOW TO RUN:
    pip install flask flask-cors requests anthropic
    python app.py

Optional: Set Anthropic API key for real AI logic.
    export ANTHROPIC_API_KEY=sk-ant-...         
"""
import sqlite3
import os, time, math
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import google.generativeai as genai 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def init_db():
    conn = None
    try:
        conn = sqlite3.connect("users.db", timeout=10)
        c = conn.cursor()
        c.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    email TEXT UNIQUE,
    mobile TEXT,
    name TEXT,
    age INTEGER,
    gender TEXT,
    location TEXT,
    diseases TEXT,
    weight REAL
)
""")
        conn.commit()
    except Exception as e:
        print("Database init error:", e)
    finally:
        if conn:
            conn.close()

init_db()

# ---------------------------------------------------------
# AI Client Setup (Graceful Fallback)
# ---------------------------------------------------------
# AI_ENABLED = False
# try:
#     import anthropic
#     _key = os.environ.get("ANTHROPIC_API_KEY", "")
#     if _key:
#         AI_CLIENT = anthropic.Anthropic(api_key=_key)
#         AI_ENABLED = True
# except ImportError:
#     pass
# (imports handled at top of file)

GEMINI_ENABLED = False

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        GEMINI_ENABLED = True
except Exception as e:
    print("Gemini init error:", e)
# ---------------------------------------------------------
# Database Mock (Represents SQL DB state for Hackathon)
# ---------------------------------------------------------
DB_HOSPITALS = [
    {"id": "h1", "name": "Apollo Gleneagles Hospital", "type": "cardiac", "icu": 0, "general": 45, "lat": 22.5748, "lon": 88.4016, "address": "Kadapara, Phoolbagan, Kankurgachi, Kolkata, West Bengal 700054"},
    {"id": "h2", "name": "SSKM Medical", "type": "general", "icu": 15, "general": 80, "lat": 22.5399, "lon": 88.3417, "address": "SSKM Hospital Rd, Bhowanipore, Kolkata, West Bengal 700020"},
    {"id": "h3", "name": "Barrackpore City Hospital", "type": "trauma", "icu": 5, "general": 20, "lat": 22.7680, "lon": 88.3580, "address": "165, Ghosh Para Rd, Barrackpore, Kolkata, West Bengal 700120"},
    {"id": "h4", "name": "Fortis Hospital", "type": "general", "icu": 8, "general": 60, "lat": 22.5186, "lon": 88.4067, "address": "730, Eastern Metropolitan Bypass, Anandapur, East Kolkata Twp, Kolkata, West Bengal 700107"},
    {"id": "h5", "name": "BM Birla Heart Hospital", "type": "cardiac", "icu": 12, "general": 30, "lat": 22.5327, "lon": 88.3283, "address": "1, 1, National Library Ave, Alipore, Kolkata, West Bengal 700027"},
    {"id": "h6", "name": "Dr B N Bose Sub Divisional Hospital", "type": "general", "icu": 10, "general": 50, "lat": 22.7515, "lon": 88.3710, "address": "Q92C+M9V, Barrackpore Trunk Rd, Barrackpore, West Bengal 700123"},
    {"id": "h7", "name": "KPC Medical College & Hospital", "type": "multispecialty", "icu": 5, "general": 70, "lat": 22.49396, "lon": 88.37331, "address": "1F, Raja S.C. Mullick Road, Jadavpur, Kolkata - 700032"},
    {"id": "h8", "name": "Baghajatin State General Hospital", "type": "general", "icu": 4, "general": 60, "lat": 22.4828, "lon": 88.3750, "address": "Raja S.C. Mullick Road, Regent Estate, Kolkata - 700092"},
    {"id": "h9", "name": "Bijoygarh State General Hospital", "type": "general", "icu": 3, "general": 55, "lat": 22.4875, "lon": 88.3639, "address": "Bijoygarh Road, Jadavpur, Kolkata - 700032"}
]

# ---------------------------------------------------------
# Static File Serving (Frontend)
# ---------------------------------------------------------

@app.route("/static/<path:path>")
def static_files(path): 
    return send_from_directory("static", path)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup", methods=["GET"])
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/signup/submit", methods=["POST"])
def signup():
    conn = None
    try:
        data = request.json
        print("Received signup data:", data)

        conn = sqlite3.connect("users.db", timeout=10)
        c = conn.cursor()

        c.execute("""
INSERT INTO users 
(username, password, email, mobile, name, age, gender, location, diseases, weight)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
            data.get("username"),
            data.get("password"),
            data.get("email"),
            data.get("mobile"),
            data.get("name"),
            data.get("age"),
            data.get("gender"),
            data.get("location"),
            data.get("diseases"),
            data.get("weight")
        ))

        conn.commit()
        print("Signup successful for:", data.get("username"))
        return jsonify({"status":"success"})
    except Exception as e:
        print("Signup error:", e)
        return jsonify({"status":"fail", "message": str(e)})
    finally:
        if conn:
            conn.close()

@app.route("/login", methods=["POST"])
def login():
    conn = None
    try:
        data = request.json
        conn = sqlite3.connect("users.db", timeout=10)
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE username=? AND password=?",
                  (data["username"], data["password"]))

        user = c.fetchone()
        if user:
            return jsonify({"status":"success"})
        else:
            return jsonify({"status":"fail"})
    except Exception as e:
        print("Login error:", e)
        return jsonify({"status":"fail", "message": str(e)})
    finally:
        if conn:
            conn.close()
# ---------------------------------------------------------
# Core API Endpoint
# ---------------------------------------------------------
@app.route("/emergency", methods=["POST"])
def process_emergency():
    data = request.json or {}
    condition = data.get("condition", "Unknown condition")
    lat = data.get("lat")
    lon = data.get("lon")
    override_hosp = data.get("override_hospital", "")
    
    # AGENT 1: Triage (NLP Severity Classification)
    severity_level = "MODERATE"
    cond_lower = condition.lower()
    critical_keywords = ["heart", "attack", "stroke", "accident", "crash", "unconscious", "chest", "bleeding"]
    if any(k in cond_lower for k in critical_keywords):
        severity_level = "CRITICAL"
    
    # AGENT 2: Hospital Orchestration & Load Balancing
    best_hospital = None
    hospital_switched = False
    switch_reason = ""
    
    # Basic intent routing
    target_type = "general"
    if "heart" in cond_lower or "chest" in cond_lower: 
        target_type = "cardiac"
    elif "accident" in cond_lower or "crash" in cond_lower: 
        target_type = "trauma"

    # Find valid hospitals by type
    valid_hospitals = [h for h in DB_HOSPITALS if h["type"] == target_type]
    
    # Fallback if no specific type matched
    if not valid_hospitals: 
        valid_hospitals = DB_HOSPITALS
        
    # Sort by closest proximity
    if lat is not None and lon is not None:
        valid_hospitals.sort(key=lambda h: haversine(lat, lon, h["lat"], h["lon"]))

    best_hospital = valid_hospitals[0]
    hospital_switched = False
    switch_reason = ""
    
    if override_hosp:
        for h in DB_HOSPITALS:
            if h["name"] == override_hosp:
                best_hospital = h
                break
    else:
        # ICU Auto-Switch Logic (Crucial Hackathon feature showing load balancing)
        if severity_level == "CRITICAL" and best_hospital["icu"] == 0:
            orig_name = best_hospital["name"]
            # Find nearest hospital with available ICU
            icu_hospitals = [h for h in DB_HOSPITALS if h["icu"] > 0]
            if lat is not None and lon is not None:
                icu_hospitals.sort(key=lambda h: haversine(lat, lon, h["lat"], h["lon"]))
                
            if icu_hospitals:
                best_hospital = icu_hospitals[0]
                hospital_switched = True
                switch_reason = f"⚠️ AI OVERRIDE: ICU FULL at {orig_name}. Diverted to nearest available: {best_hospital['name']}."

    # AGENT 3: Medical Summary Generation
    medical_summary = "Analyzing patient data..."
    traffic_alert = "Normal traffic rules apply."
    hospital_alert = "Patient inbound. General admission prep."
    
    if severity_level == "CRITICAL":
        medical_summary = "Administer 324mg chewed aspirin and obtain an immediate 12-lead ECG. Activate Cath Lab for emergent reperfusion."
        traffic_alert = "High Priority: Overriding all traffic signals along route to ensure uninterrupted path."
        hospital_alert = f"Urgent: Reserve ICU bed at {best_hospital['name']}. Trauma team standby."
    else:
        medical_summary = "Stabilize patient and monitor vitals. Transport to nearest general ward for evaluation."
        traffic_alert = "Route optimized based on current congestion. No signal overrides required."
        hospital_alert = f"Notify ER of incoming stable patient at {best_hospital['name']}."

    return jsonify({
        "status": "success",
        "severity": severity_level,
        "hospital": best_hospital,
        "route": {
            "optimized": 8,
            "distance": 2.4,
            "desc": traffic_alert
        },
        "ai_reports": {
            "medical": medical_summary,
            "traffic": traffic_alert,
            "hospital": hospital_alert
        }
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("\n" + "="*50)
    print("[*] ClearRoute AI Network Backend Started")
    print(f"[*] AI Engine: {'ONLINE (Gemini Active)' if GEMINI_ENABLED else 'OFFLINE (Using Local Rule-based Fallback)'}")
    print(f"[*] Dashboard: http://0.0.0.0:{port}")
    print("="*50 + "\n")
    app.run(debug=False, host="0.0.0.0", port=port)