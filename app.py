import sqlite3
import os, time, math
from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import google.generativeai as genai 
from twilio.rest import Client
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

twilio_client = Client(
    os.getenv("TWILIO_SID"),
    os.getenv("TWILIO_AUTH")
)

GEMINI_ENABLED = False

try:
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-3-flash-preview")
        GEMINI_ENABLED = True
except Exception as e:
    print("Gemini init error:", e)
# ---------------------------------------------------------
# Database Mock (Represents SQL DB state for Hackathon)
# ---------------------------------------------------------
import urllib.request
import urllib.parse
import json

def get_dynamic_hospitals(lat, lon, radius=5000):
    if lat is None or lon is None:
        lat, lon = 22.5726, 88.3639 # Fallback to Kolkata if no coordinates

    try:
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json];
        node["amenity"="hospital"](around:{radius},{lat},{lon});
        out 10;
        """
        data = urllib.parse.urlencode({'data': overpass_query}).encode('utf-8')
        req = urllib.request.Request(overpass_url, data=data)
        with urllib.request.urlopen(req, timeout=4) as response:
            result = json.loads(response.read().decode('utf-8'))
            
        hospitals = []
        for idx, element in enumerate(result.get('elements', [])):
            tags = element.get('tags', {})
            name = tags.get('name', f"Local Hospital {idx+1}")
            addr = tags.get('addr:street', f"Near {lat:.4f}, {lon:.4f}")
            hospitals.append({
                "id": f"dh{idx}",
                "name": name,
                "type": "general",
                "icu": 5 + (idx % 10),
                "general": 20 + (idx * 5),
                "lat": element['lat'],
                "lon": element['lon'],
                "address": addr
            })
            
        if hospitals:
            hospitals[0]["icu"] = 0 # Force one to have 0 ICU for diversion demo
            return hospitals
            
    except Exception as e:
        print(f"Overpass API error: {e}")
    
    # Fallback: spawn dummy hospitals around lat, lon
    return [
        {"id": "f1", "name": "City Central Medical", "type": "general", "icu": 0, "general": 45, "lat": lat + 0.01, "lon": lon + 0.01, "address": "123 Main St"},
        {"id": "f2", "name": "Metro Trauma Center", "type": "trauma", "icu": 15, "general": 80, "lat": lat - 0.02, "lon": lon + 0.015, "address": "45 Emergency Ave"},
        {"id": "f3", "name": "Global Care Hospital", "type": "cardiac", "icu": 5, "general": 20, "lat": lat + 0.015, "lon": lon - 0.01, "address": "90 Heart Blvd"},
        {"id": "f4", "name": "Sunrise General", "type": "general", "icu": 8, "general": 60, "lat": lat - 0.01, "lon": lon - 0.02, "address": "10 Sunrise Dr"}
    ]

# ---------------------------------------------------------
# Static File Serving (Frontend)
# ---------------------------------------------------------

@app.route("/static/<path:path>")
def static_files(path): 
    return send_from_directory("static", path)

@app.route("/api/server-location")
def server_location():
    """Fetch location using multiple IP services via built-in urllib."""
    import urllib.request
    import json as _json

    services = [
        {
            "url": "http://ip-api.com/json/?fields=status,lat,lon,city,regionName,country",
            "parse": lambda d: (d["lat"], d["lon"], f"{d['city']}, {d['regionName']}, {d['country']}", "ip-api")
                               if d.get("status") == "success" and d.get("lat") else None
        },
        {
            "url": "https://ipinfo.io/json",
            "parse": lambda d: (float(d["loc"].split(",")[0]), float(d["loc"].split(",")[1]),
                                f"{d.get('city','')}, {d.get('region','')}, {d.get('country','')}",
                                "ipinfo")
                               if "loc" in d else None
        },
        {
            "url": "https://ipapi.co/json/",
            "parse": lambda d: (d["latitude"], d["longitude"],
                                f"{d.get('city','')}, {d.get('region','')}, {d.get('country_name','')}",
                                "ipapi.co")
                               if d.get("latitude") else None
        },
    ]

    for svc in services:
        try:
            req_obj = urllib.request.Request(svc["url"], headers={"User-Agent": "ClearRoute/1.0"})
            with urllib.request.urlopen(req_obj, timeout=6) as resp:
                data = _json.loads(resp.read().decode())
            result = svc["parse"](data)
            if result:
                lat, lon, address, source = result
                return jsonify({"success": True, "lat": lat, "lon": lon, "address": address, "source": source})
        except Exception as e:
            print(f"[location] {svc['url']} failed: {e}")
            continue

    return jsonify({"success": False, "error": "All location sources failed"})

def send_hospital_alert(message):
    try:
        twilio_client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE"),
            to=os.getenv("HOSPITAL_PHONE")
        )
        print("Hospital SMS sent")
    except Exception as e:
        print("SMS Error:", e)

def make_hospital_call():
    try:
        call = twilio_client.calls.create(
            twiml='''
<Response>
    <Say voice="alice">
        Emergency alert. Critical patient incoming. 
        Please prepare emergency response team immediately.
    </Say>
</Response>
''',
            from_=os.getenv("TWILIO_PHONE"),
            to=os.getenv("HOSPITAL_PHONE")
        )

        print("Call initiated:", call.sid)
    except Exception as e:
        print("Call Error:", e)

def send_traffic_alert(message):

    try:
        twilio_client.messages.create(
            body=message,
            from_=os.getenv("TWILIO_PHONE"),
            to=os.getenv("TRAFFIC_PHONE")
        )

        print("Traffic alert sent")

    except Exception as e:
        print("Traffic SMS Error:", e)

@app.route("/")
def home():
    return render_template("login.html")

@app.route("/signup-page")
def signup_page():
    return render_template("signup.html")

@app.route("/dashboard")
def dashboard():
    return render_template("index.html")

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json

    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    try:
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
        return jsonify({"status":"success"})
    except sqlite3.IntegrityError:
        return jsonify({"status":"fail", "message": "Username or email already exists."})
    except Exception as e:
        return jsonify({"status":"fail", "message": str(e)})
    finally:
        conn.close()
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
    
    # Fetch dynamic hospitals near user
    local_hospitals = get_dynamic_hospitals(lat, lon)
    
    # Basic intent routing
    target_type = "general"
    if "heart" in cond_lower or "chest" in cond_lower: 
        target_type = "cardiac"
    elif "accident" in cond_lower or "crash" in cond_lower: 
        target_type = "trauma"

    # Find valid hospitals by type (mocked in dynamic fetch)
    valid_hospitals = [h for h in local_hospitals if h["type"] == target_type]
    
    # Fallback if no specific type matched
    if not valid_hospitals: 
        valid_hospitals = local_hospitals
        
    # Sort by closest proximity
    if lat is not None and lon is not None:
        valid_hospitals.sort(key=lambda h: haversine(lat, lon, h["lat"], h["lon"]))

    best_hospital = valid_hospitals[0]
    hospital_switched = False
    switch_reason = ""
    
    if override_hosp:
        DB_HOSPITALS = [
            {"name": "Apollo Gleneagles", "icu":0, "general":45, "address":"58, Canal Circular Rd, Kadapara, Phoolbagan, Kankurgachi, Kolkata, West Bengal 700054", "lat":22.5748, "lon":88.4016},
            {"name": "SSKM Medical", "icu":15, "general":80, "address":"SSKM Hospital Rd, Bhowanipore, Kolkata, West Bengal 700020", "lat":22.5399, "lon":88.3417},
            {"name": "Barrackpore City Hospital", "icu":5, "general":20, "address":"Hospital, 165, Ghosh Para Rd, Barrackpore, Kolkata, West Bengal 700120", "lat":22.7680, "lon":88.3580},
            {"name": "Fortis Hospital", "icu":8, "general":60, "address":"730, Eastern Metropolitan Bypass, Anandapur, East Kolkata Twp, Kolkata, West Bengal 700107", "lat":22.5186, "lon":88.4067},
            {"name": "BM Birla Heart", "icu":12, "general":30, "address":"1, 1, National Library Ave, Alipore, Kolkata, West Bengal 700027", "lat":22.5327, "lon":88.3283},
            {"name": "Dr B N Bose Sub Divisional Hospital", "icu":10, "general":50, "address":"Q92C+M9V, Barrackpore Trunk Rd, Barrackpore, West Bengal 700123", "lat":22.7515, "lon":88.3710},
            {"name": "KPC Medical College & Hospital", "icu": 5, "general": 70, "address": "1F, Raja S.C. Mullick Road, Jadavpur, Kolkata - 700032", "lat": 22.49396, "lon": 88.37331},
            {"name": "Baghajatin State General Hospital", "icu": 4, "general": 60, "address": "Raja S.C. Mullick Road, Regent Estate, Kolkata - 700092", "lat": 22.4828, "lon": 88.3750},
            {"name": "Bijoygarh State General Hospital", "icu": 3, "general": 55, "address": "Bijoygarh Road, Jadavpur, Kolkata - 700032", "lat": 22.4875, "lon": 88.3639}
        ]
        
        found = False
        # 1. Try to find in the static list for exact real-world coordinates
        for h in DB_HOSPITALS:
            if h["name"] == override_hosp:
                best_hospital = h
                found = True
                break
                
        # 2. If not found in static list, check dynamic list
        if not found:
            for h in local_hospitals:
                if h["name"] == override_hosp:
                    best_hospital = h
                    found = True
                    break
                    
        # 3. Create mock hospital only if it's completely unknown
        if not found:
            best_hospital = {
                "id": "override_custom",
                "name": override_hosp,
                "type": "general",
                "icu": 10,
                "general": 50,
                "lat": (lat + 0.015) if lat else 22.58,
                "lon": (lon + 0.015) if lon else 88.37,
                "address": "Custom selected facility"
            }
    else:
        # ICU Auto-Switch Logic (Crucial Hackathon feature showing load balancing)
        if severity_level == "CRITICAL" and best_hospital["icu"] == 0:
            orig_name = best_hospital["name"]
            # Find nearest hospital with available ICU
            icu_hospitals = [h for h in local_hospitals if h["icu"] > 0]
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
        hospital_alert = f"Urgent: Reserve ICU bed for with {condition} at {best_hospital['name']} . Trauma team standby."
        send_hospital_alert(hospital_alert)
        make_hospital_call()
        send_traffic_alert(traffic_alert)
    
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
    print("ClearRoute AI Network Backend Started")
    print(f"AI Engine: {'ONLINE (Claude Active)' if GEMINI_ENABLED else 'OFFLINE (Using Local Rule-based Fallback)'}")
    print("Dashboard: http://127.0.0.1:5001")
    print("="*50 + "\n")
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=False, host="0.0.0.0", port=port)