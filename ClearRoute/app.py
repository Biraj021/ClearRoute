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
from flask import Flask, request, jsonify, send_from_directory
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
    conn = sqlite3.connect("users.db")
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
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

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
    {"id": "h1", "name": "Apollo Gleneagles", "type": "cardiac", "icu": 0, "general": 45, "lat": 22.5748, "lon": 88.4016, "address": "58, Canal Circular Rd, Kadapara, Phoolbagan, Kankurgachi, Kolkata, West Bengal 700054"},
    {"id": "h2", "name": "SSKM Medical", "type": "general", "icu": 15, "general": 80, "lat": 22.5399, "lon": 88.3417, "address": "SSKM Hospital Rd, Bhowanipore, Kolkata, West Bengal 700020"},
    {"id": "h3", "name": "Barrackpore City Hospital", "type": "trauma", "icu": 5, "general": 20, "lat": 22.7680, "lon": 88.3580, "address": "Hospital, 165, Ghosh Para Rd, Barrackpore, Kolkata, West Bengal 700120"},
    {"id": "h4", "name": "Fortis Hospital", "type": "general", "icu": 8, "general": 60, "lat": 22.5186, "lon": 88.4067, "address": "730, Eastern Metropolitan Bypass, Anandapur, East Kolkata Twp, Kolkata, West Bengal 700107"},
    {"id": "h5", "name": "BM Birla Heart", "type": "cardiac", "icu": 12, "general": 30, "lat": 22.5327, "lon": 88.3283, "address": "1, 1, National Library Ave, Alipore, Kolkata, West Bengal 700027"},
    {"id": "h6", "name": "Dr B N Bose Sub Divisional Hospital", "type": "general", "icu": 10, "general": 50, "lat": 22.7515, "lon": 88.3710, "address": "Q92C+M9V, Barrackpore Trunk Rd, Barrackpore, West Bengal 700123"}
]

# ---------------------------------------------------------
# Static File Serving (Frontend)
# ---------------------------------------------------------

@app.route("/static/<path:path>")
def static_files(path): 
    return send_from_directory("static", path)

@app.route("/")
def home():
    return send_from_directory("templates", "login.html")

@app.route("/signup-page")
def signup_page():
    return send_from_directory("templates", "signup.html")

@app.route("/dashboard")
def dashboard():
    return send_from_directory("templates", "index.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("""
INSERT INTO users 
(username, password, email, mobile, name, age, gender, location, diseases, weight)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    data["username"],
    data["password"],
    data["email"],
    data["mobile"],
    data["name"],
    data["age"],
    data["gender"],
    data["location"],
    data["diseases"],
    data["weight"]
))

    conn.commit()
    conn.close()

    return jsonify({"status":"success"})
@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (data["username"], data["password"]))

    user = c.fetchone()
    conn.close()

    if user:
        return jsonify({"status":"success"})
    else:
        return jsonify({"status":"fail"})
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

    # AGENT 3: Medical Summary Generation (Uses Claude if available)
    medical_summary = f"Patient inbound presenting with {condition}. Vital signs pending. Team prepare for immediate triage."
    traffic_alert = "Normal traffic rules apply."
    hospital_alert = "Patient inbound. General admission prep."
    
    if severity_level == "CRITICAL":
        traffic_alert = "High Priority: Overriding all traffic signals along route to ensure uninterrupted path."
        hospital_alert = f"Urgent: Reserve ICU bed at {best_hospital['name']}. Trauma team standby."
    
    # if GEMINI_ENABLED:
    #     try:
    #         prompt = f"You are an Emergency Medical AI. Patient report: '{condition}'. Severity: {severity_level}. Provide a concise 2-sentence clinical directive for the receiving ER team, stating what equipment or specialists to prepare."
    #         resp = AI_CLIENT.messages.create(
    #             model="claude-3-haiku-20240307", 
    #             max_tokens=100,
    #             messages=[{"role": "user", "content": prompt}]
    #         )
    #         medical_summary = resp.content[0].text.strip()
    #     except Exception as e:
    #         print(f"Anthropic API Error: {e}")

    if GEMINI_ENABLED:
        try:
            prompt = f"""
You are an Emergency Medical AI.
Patient condition: {condition}
Severity: {severity_level}

Give a short 2-line medical instruction for ER team.
"""

            response = model.generate_content(prompt)
            medical_summary = response.text

        except Exception as e:
            print("Gemini Error:", e)

    # Calculate routing metadata
    eta = 12 if severity_level == "CRITICAL" else 18
    saved = 15 if severity_level == "CRITICAL" else 5
    route_desc = "Traffic Control Notified → Police clearing route" if severity_level == "CRITICAL" else "Standard Routing Active."

    response_payload = {
        "severity": {"level": severity_level},
        "hospital": {
            "name": best_hospital["name"],
            "address": best_hospital["address"],
            "lat": best_hospital["lat"],
            "lon": best_hospital["lon"],
            "icu": best_hospital["icu"],
            "gen": best_hospital["general"],
            "switched": hospital_switched,
            "switch_reason": switch_reason
        },
        "route": {
            "optimized": eta,
            "time_saved": saved,
            "desc": route_desc
        },
        "nearby_hospitals": valid_hospitals[:4],
        "messages": {
            "medical_summary": medical_summary,
            "traffic_alert": traffic_alert,
            "hospital_alert": hospital_alert
        }
    }
    
    # Simulate processing delay to allow UI to show terminal streaming
    time.sleep(0.8) 
    
    return jsonify(response_payload)

if __name__ == "__main__":
    print("\n" + "="*50)
    print("🚀 ClearRoute AI Network Backend Started")
    print(f"🧠 AI Engine: {'ONLINE (Claude Active)' if GEMINI_ENABLED else 'OFFLINE (Using Local Rule-based Fallback)'}")
    print("🌐 Dashboard: http://127.0.0.1:5000")
    print("="*50 + "\n")
    app.run(debug=True, host="127.0.0.1", port=5000)