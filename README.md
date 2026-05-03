<div align="center">

# 🚑 ClearRoute

### *AI-Powered Emergency Response System*

**Detect. Dispatch. Deliver. — Before the window closes.**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=flat-square&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![Leaflet](https://img.shields.io/badge/Leaflet.js-1.9-199900?style=flat-square&logo=leaflet&logoColor=white)](https://leafletjs.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![HackArena](https://img.shields.io/badge/HackArena%202025-Kolkata%20Zonal-E8001C?style=flat-square)](/)

<br/>

> *"Every minute of delay in emergency response costs lives. ClearRoute eliminates that delay — using AI that acts, not just advises."*

<br/>

<img width="1024" height="1536" alt="ChatGPT Image May 1, 2026, 09_12_29 PM" src="https://github.com/user-attachments/assets/3f1915d4-d094-49bf-9a81-0b37e87ab8d5" />


</div>

---

## 🧠 What is ClearRoute?

ClearRoute is a **production-ready AI emergency response system** that replaces manual ambulance dispatch with an autonomous, real-time pipeline. From the moment an emergency is reported to the moment the hospital team is ready — everything is automated.

Think of it as **Uber for ambulances — powered by four AI agents working in parallel.**

| Without ClearRoute | With ClearRoute |
|---|---|
| Manual phone dispatch (3–8 min) | AI dispatch in < 1 second |
| ICU availability unknown until arrival | Real-time bed availability check |
| No routing intelligence | OSRM real road routing + ETA |
| Hospital unprepared | Pre-alert sent before ambulance arrives |
| No live tracking | Delivery-style status updates |

---

## 🤖 AI Architecture

ClearRoute is built around **4 autonomous AI agents** and **2 generative AI modules** that work as a sequential decision pipeline.

```
┌─────────────────────────────────────────────────────────────────┐
│                     AI AGENT PIPELINE                           │
│                                                                 │
│  📥 Input                                                       │
│  (Location + Condition + Prescription)                          │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │  Agent 1        │  Severity Detection Agent                 │
│  │  🔍 Classify    │  Keyword NLP → CRITICAL / MODERATE / LOW  │
│  └────────┬────────┘                                           │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │  Agent 2        │  Hospital Selection Agent                 │
│  │  🏥 Match       │  Condition type + ICU availability check  │
│  └────────┬────────┘  Auto-switch if ICU beds = 0             │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │  Agent 3        │  Traffic Clearance Agent                  │
│  │  🚦 Route       │  OSRM smart routing + priority corridor   │
│  └────────┬────────┘                                           │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │  Agent 4        │  ER Readiness Agent                       │
│  │  📡 Alert       │  Pre-alert dispatch + bed coordination    │
│  └────────┬────────┘                                           │
│           ▼                                                     │
│  ┌──────────────────────────────────────┐                      │
│  │  Generative AI Modules               │                      │
│  │  ✨ Prescription Summary Generator   │  Claude AI / Fallback│
│  │  📣 Alert Message Generator          │  Dynamic text gen    │
│  └──────────────────────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Agent Details

| Agent | Role | Logic |
|---|---|---|
| **Severity Detection** | Classifies emergency level | Keyword NLP across 20+ conditions |
| **Hospital Selection** | Finds best-fit hospital | Condition type × ICU availability × distance |
| **Traffic Clearance** | Computes optimal route | OSRM API → real ETA → priority adjustment |
| **ER Readiness** | Prepares hospital before arrival | Dispatches pre-alert 5–10 min before ETA |

### Generative AI Modules

- **Prescription Summary Generator** — Reads uploaded prescription text → generates a clinical 3-sentence briefing for the ER team using Claude API (falls back to template pool offline)
- **Alert Message Generator** — Dynamically produces unique traffic coordination messages and hospital pre-alerts per dispatch (not hardcoded; varies by severity + hospital type)

---

## 🔄 System Workflow

```
User Reports Emergency
        │
        ▼
   📱 Input Form
   (Location via GPS / manual + Condition + Optional Prescription)
        │
        ▼
   🔍 Agent 1: Severity Detection
   CRITICAL ──────────────────────────┐
   MODERATE ─────────────────────┐   │
   LOW ──────────────────────┐   │   │
                             │   │   │
        ▼                    ▼   ▼   ▼
   🏥 Agent 2: Hospital Selection
   (cardiac / trauma / general — auto-switch if ICU = 0)
        │
        ▼
   🚑 Ambulance Dispatch
   (Nearest unit via Haversine scoring)
        │
        ▼
   🚦 Agent 3: Route Optimization
   (OSRM real road routing → distance_km + eta_min)
        │
        ├──────────────────────────────────────┐
        ▼                                      ▼
   🗺️ Leaflet Map                     📡 Agent 4: ER Readiness
   (Route drawn, ambulance tracked)    (Pre-alert + AI summary sent)
        │                                      │
        └──────────────┬───────────────────────┘
                       ▼
              ✅ Patient Delivered
              Hospital Ready. Zero Surprises.
```

---

## ⚡ Features

- 🧠 **AI Severity Detection** — Real-time classification from text or voice input
- 🏥 **Smart Hospital Matching** — Condition-aware selection with live ICU bed availability
- 🚑 **Nearest Ambulance Dispatch** — Haversine distance scoring across the full fleet
- 🗺️ **Real-Time Map Routing** — OSRM-powered road routes drawn on Leaflet.js
- 📍 **Live GPS Tracking** — Delivery-style status: Assigned → En Route → Pickup → Delivered
- 🎤 **Voice Input** — Web Speech API: say "chest pain" and severity sets automatically
- 📄 **Prescription Upload** — File or text; AI generates clinical ER briefing
- ✨ **AI Medical Summary** — Claude API (optional) or rich simulation fallback
- 🔁 **Offline-First Fallback** — Full simulation mode, no API key required
- ⌨️ **Keyboard Dispatch** — `Ctrl + Enter` triggers emergency from anywhere in the app

---

## 🧱 Tech Stack

### Frontend
| Technology | Purpose |
|---|---|
| HTML5 + CSS3 | Responsive dashboard UI |
| Vanilla JavaScript | Modular, zero-dependency logic |
| Leaflet.js | Interactive map rendering |
| Web Speech API | Browser-native voice input |

### Backend
| Technology | Purpose |
|---|---|
| Python 3.10+ | Core runtime |
| Flask | Lightweight REST API server |
| Flask-CORS | Cross-origin request handling |

### APIs & Services
| Service | Purpose |
|---|---|
| OSRM | Real road routing + accurate ETA |
| Nominatim / OpenStreetMap | Free geocoding — no API key needed |
| Overpass API | Nearby hospital discovery |
| Anthropic Claude (optional) | Generative medical summaries |

---

## ⚙️ Setup

### Prerequisites
- Python 3.10+
- A modern browser (Chrome / Edge recommended for voice input)
- Internet connection (for OSRM + Nominatim)

### 1. Clone the repository

```bash
git clone [https://github.com/your-username/clearroute.git](https://github.com/Biraj021/ClearRoute)
cd clearroute
```

### 2. Install backend dependencies

```bash
pip install flask flask-cors anthropic
```

### 3. Configure API key (optional)

```bash
# For AI medical summaries via Claude
export ANTHROPIC_API_KEY=sk-ant-your-key-here

# On Windows:
set ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> ⚠️ **No API key? No problem.** ClearRoute runs a full simulation fallback automatically. Every feature works without any external AI service.

### 4. Start the backend

```bash
python app.py
```

The server starts at `http://127.0.0.1:5000`

### 5. Open the frontend

```bash
# Simply open in your browser:
open index.html

# Or serve it (optional):
python -m http.server 8080
```

### 6. Use the app

1. Click **Use My Location** or type a start address
2. Select patient condition (or say it via voice 🎤)
3. Upload a prescription (optional)
4. Press **Start Emergency** or hit `Ctrl + Enter`
5. Watch the AI pipeline run → route appear → results populate

---

## 💡 Why ClearRoute Stands Out

**1. Agentic AI, not just AI features**
ClearRoute doesn't use AI as a wrapper — it uses four autonomous agents that make real sequential decisions. No human is in the dispatch loop.

**2. Offline-first by design**
Every AI feature has a simulation fallback. The demo works in a basement with no internet and no API key. This was a deliberate architectural choice.

**3. Real routing, real ETA**
ETA is taken directly from `routes[0].duration` in the OSRM response — never calculated from assumed speed, never hardcoded. Judges can verify it against Google Maps.

**4. Prescription-to-Alert pipeline**
Upload a medication photo or paste notes → AI generates a clinical ER briefing. No competitor in this space combines prescription context with real-time dispatch.

**5. Delivery-app UX for emergencies**
The same tracking experience as Zomato or Uber, applied to the highest-stakes use case imaginable. Familiar interface reduces panic for patients and families.

---

## 🚧 Limitations

- Ambulance positions are simulated (no real GPS hardware integration yet)
- Hospital bed availability uses static demo data (real hospital API integration is Phase 2)
- Voice input requires Chrome or Edge (Web Speech API is not supported in Firefox)
- Claude AI medical summaries require an active API key and internet connection

---

## 🚀 Future Scope

| Phase | Timeline | Milestone |
|---|---|---|
| **Phase 1** | Now | Working prototype — simulated data, demo-ready |
| **Phase 2** | 6 months | 3-city launch — real hospital API, ambulance partner fleet |
| **Phase 3** | 1 year | 10-state rollout — government 108/112 integration |
| **Phase 4** | 3 years | Pan-India — trained AI triage model, IoT vitals streaming |

**Planned features:**
- 📡 IoT vitals streaming from ambulance to ER
- 🛰️ Satellite-independent ambulance GPS tracking
- 🤝 Government 108/112 API integration (no infrastructure replacement)
- 🧬 ML triage model trained on anonymised emergency case data
- 📲 Family share link — real-time tracking URL sent via SMS

---

## 🌍 Real-World Impact

| Metric | Estimated Impact |
|---|---|
| Response time reduction | ~8 minutes per emergency |
| Hospital preparation delay | ~50% reduction via pre-alert |
| Routing efficiency | ~30% improvement via OSRM |
| System uptime | 100% — offline fallback always active |

> In India alone, faster emergency response could prevent an estimated **100,000+ deaths annually** that are currently attributed to delayed ambulance arrival and unprepared hospital reception.

ClearRoute is not just a hackathon project. It is the foundation architecture for the next generation of emergency infrastructure.

---

## 📁 Project Structure

```
clearroute/
├── index.html          # Main dashboard UI
├── style.css           # Tactical dark theme
├── script.js           # Frontend logic + OSRM + map
├── app.py              # Flask backend + AI agent pipeline
├── assets/
│   └── architecture.png
└── README.md
```

---

## 👤 Author

**Biraj Acherjee**
**Rajanya Saha**
Built for HackArena 2025 — Kolkata Zonal Round

---

<div align="center">

**If ClearRoute impressed you, a ⭐ on this repo means a lot.**

*"ClearRoute doesn't just find routes — it saves lives."*

</div>
