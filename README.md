# 🚑 ClearRoute

### AI-Powered Emergency Response System

> **Smart • Fast • Life-Saving**

ClearRoute is an intelligent emergency response platform that uses AI to **analyze medical conditions, select the best hospital, and generate the fastest route in real-time** — helping reduce critical response time during emergencies.

---

## 🌟 Overview

In emergency situations, every second matters.
ClearRoute automates decision-making to ensure patients reach the **right hospital, at the right time, via the fastest route**.

---

## ⚡ Core Capabilities

* 🧠 **AI Severity Detection**
  Automatically classifies cases into Critical, Moderate, or Low

* 🏥 **Smart Hospital Selection**
  Chooses the most suitable hospital based on condition & ICU availability

* 🛣️ **Real-Time Route Optimization**
  Uses OSRM to calculate the fastest road route

* 📍 **Live Location Detection**
  GPS + manual input with reverse geocoding

* 🗺️ **Interactive Map Interface**
  Built using Leaflet.js with dynamic markers and routes

* 🎤 **Voice-Based Input**
  Detect conditions using speech recognition

* 📄 **Prescription Upload**
  Share medical notes with AI for enhanced response

* 🔁 **AI + Fallback Mode**
  Works with backend AI or browser simulation

---

## 🔄 Workflow

```
User Input → AI Analysis → Hospital Selection → Route Optimization → Emergency Dispatch
```

**Current Flow:**
Patient → Hospital (Direct Intelligent Routing)

---

## 🧱 Tech Stack

**Frontend**

* HTML, CSS, JavaScript
* Leaflet.js

**Backend**

* Python (Flask)
* REST APIs

**AI Layer**

* Claude API (optional)
* Local Simulation Engine

**External Services**

* OpenStreetMap (Nominatim)
* OSRM Routing Engine

---

## ⚙️ Local Setup

```bash
git clone https://github.com/YOUR_USERNAME/ClearRoute-AI-Emergency-System.git
cd ClearRoute-AI-Emergency-System

pip install flask flask-cors anthropic
python app.py
```

Open in browser:
👉 http://127.0.0.1:5000

---

## 💡 What Makes It Unique

* ⚡ Real-time AI decision pipeline
* 🧭 Intelligent routing instead of static navigation
* 🔄 Works even without backend AI
* 🎯 Focused on real-world emergency impact

---

## 🚧 Current Limitations

* No ambulance dispatch system yet
* No real-time ambulance tracking
* No traffic signal integration

---

## 🚀 Future Vision

* 🚑 Smart Ambulance Assignment System
* 📡 Live Tracking (Uber-style)
* 🚦 AI Traffic Signal Control
* 📱 Mobile App for Emergency Drivers
* 🌍 Smart City Integration

---

## 🌍 Impact

* ⏱️ Reduces emergency response time
* ❤️ Increases survival chances
* 🤖 Automates critical decisions
* 🏙️ Scalable for smart cities

---

## 👨‍💻 Author

Biraj Acherjee
Rajanya Saha

---

## ⭐ Support

If you find this project useful, consider giving it a star ⭐
