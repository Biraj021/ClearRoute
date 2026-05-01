# 🚑 ClearRoute – AI Emergency Response System

ClearRoute is an **AI-powered emergency response system** designed to reduce response time by intelligently selecting the best hospital and optimizing routes in real-time.

---

## 🚀 Features

* 🧠 AI-based Severity Detection (Critical / Moderate / Low)
* 🏥 Smart Hospital Selection (based on condition & ICU availability)
* 🛣️ Real-Time Route Optimization using OSRM
* 📍 Live Location Detection (GPS + manual input)
* 🗺️ Interactive Map with Leaflet.js
* 🎤 Voice Input for emergency conditions
* 📄 Prescription Upload & AI Medical Summary
* 🔁 Backend AI + Browser Simulation fallback
* ⚡ Dynamic UI with real-time status updates

---

## 🔄 System Flow

User → AI Analysis → Hospital Selection → Route Optimization → Dispatch Info

(Current Version: Direct routing from Patient → Hospital)

---

## 🧱 Tech Stack

### Frontend

* HTML, CSS, JavaScript
* Leaflet.js (Map Rendering)

### Backend

* Python (Flask)
* REST API

### AI Integration

* Claude API (optional)
* Local Simulation Logic

### APIs Used

* OpenStreetMap (Nominatim) – Geocoding
* OSRM – Route Optimization

---

## ⚙️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/ClearRoute-AI-Emergency-System.git
cd ClearRoute-AI-Emergency-System
```

### 2. Install dependencies

```bash
pip install flask flask-cors anthropic
```

### 3. Run the backend

```bash
python app.py
```

### 4. Open in browser

http://127.0.0.1:5000

---

## 💡 Key Highlights

* AI-driven emergency decision system
* Intelligent hospital selection
* Real-time routing and visualization
* Works even without AI backend (fallback mode)

---

## 🚧 Limitations (Current Version)

* ❌ No real-time ambulance tracking
* ❌ No nearest ambulance dispatch yet
* ❌ No live traffic signal control integration

---

## 🚀 Future Enhancements

* 🚑 Nearest Ambulance Assignment System
* 📡 Live Ambulance Tracking (like Uber/Zomato)
* 🚦 Smart Traffic Signal Integration
* 📱 Mobile App for Drivers
* 🌍 Multi-city scalability

---

## 🌍 Impact

* ⏱️ Faster emergency response
* ❤️ Potential to save lives
* 🤖 Automation of critical decisions
* 📈 Scalable for smart city infrastructure

---

## 👨‍💻 Author

Your Name

---

## ⭐ Support

If you like this project, give it a star ⭐ on GitHub!
