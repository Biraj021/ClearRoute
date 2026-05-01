"use strict";

const BASE_URL = window.location.origin;
const BACKEND = `${BASE_URL}/emergency`;

// ==========================================
// 1. INITIALIZATION & MAP SETUP
// ==========================================
const map = L.map("map", { zoomControl: false }).setView([22.5726, 88.3639], 13);
L.tileLayer('https://{s}.google.com/vt/lyrs=m&x={x}&y={y}&z={z}', {
  maxZoom: 20,
  subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
  attribution: 'Map data © Google'
}).addTo(map);

// State Variables
let mapRoute = null;
let mapRouteGlow = null;
let markers = [];
let ambulanceMarker = null;
let trafficLightMarkers = [];
let animInterval = null;

// Clock Updater
setInterval(() => {
  document.getElementById("clock").textContent = new Date().toLocaleTimeString("en-US", {hour12:false});
}, 1000);

// ==========================================
// 2. EVENT LISTENERS
// ==========================================
document.getElementById("btnGPS").onclick = getLiveLocation;
document.getElementById("btnDispatch").onclick = handleDispatch;
document.getElementById("btnVoice").onclick = startVoice;
document.addEventListener("keydown", (e) => { 
  if (e.key === "Enter" && e.ctrlKey) handleDispatch(); 
});

const dropzone = document.getElementById("rxDropzone");
const fileInput = document.getElementById("rxFileInput");
const dzTitle = document.getElementById("rxDzTitle");

dropzone.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  if (e.target.files && e.target.files.length > 0) {
    dzTitle.innerText = e.target.files[0].name;
    dropzone.style.borderColor = "var(--cyan)";
    dropzone.style.background = "rgba(6, 182, 212, 0.1)";
  } else {
    dzTitle.innerText = "Upload Medical History";
    dropzone.style.borderColor = "rgba(255,255,255,0.2)";
    dropzone.style.background = "rgba(255, 255, 255, 0.03)";
  }
});

function setCondition(cond) {
  document.getElementById("condInput").value = cond;
}

// ==========================================
// 3. GPS & GEOCODING
// ==========================================
function getLocation(){
  if (!navigator.geolocation) {
    alert("Geolocation not supported by your browser");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    function(position) {
      const lat = position.coords.latitude;
      const lon = position.coords.longitude;

      document.getElementById("location").value = 
        `Lat: ${lat}, Lon: ${lon}`;
    },
    function(error) {
      if(error.code === 1){
        alert("Permission denied. Allow location access.");
      } else if(error.code === 2){
        alert("Location unavailable.");
      } else if(error.code === 3){
        alert("Request timeout.");
      } else {
        alert("Unknown error occurred.");
      }
    },
    {
      enableHighAccuracy: true,
      timeout: 10000,
      maximumAge: 0
    }
  );
}

function getLiveLocation() {
  const btn = document.getElementById("btnGPS");
  btn.style.opacity = 0.5;
  logTerminal("Requesting GPS coordinates from satellite...");
  
  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      const lat = pos.coords.latitude;
      const lon = pos.coords.longitude;
      map.setView([lat, lon], 15);
      
      const address = await reverseGeocode(lat, lon);
      document.getElementById("inputStart").value = address;
      btn.style.opacity = 1;
      logTerminal(`Acquired GPS Fix: <span class="highlight">${lat.toFixed(4)}, ${lon.toFixed(4)}</span>`);
      logTerminal(`Resolved Address: ${address}`);
    },
    (err) => { 
      logTerminal(`GPS Error: ${err.message}`);
      btn.style.opacity = 1; 
    }
  );
}

async function reverseGeocode(lat, lon) {
  try {
    const r = await fetch(`https://nominatim.openstreetmap.org/reverse?lat=${lat}&lon=${lon}&format=json`);
    const d = await r.json();
    return d.display_name.split(",").slice(0,3).join(", ");
  } catch { return `${lat.toFixed(4)}, ${lon.toFixed(4)}`; }
}

async function geocode(query) {
  const res = await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(query)}&format=json&limit=1`);
  const data = await res.json();
  if (!data || data.length===0) throw new Error("Location not found via Geocoding API");
  return [parseFloat(data[0].lat), parseFloat(data[0].lon)];
}

// ==========================================
// 4. AI VOICE ASSISTANT (WEB SPEECH API)
// ==========================================
function startVoice() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    logTerminal("ERROR: Browser does not support Web Speech API");
    return;
  }
  
  const rec = new SR();
  rec.lang = "en-US";
  document.getElementById("btnVoice").classList.add("recording");
  logTerminal("Voice interface active. Listening for symptoms...");
  
  rec.onresult = (e) => {
    const text = e.results[0][0].transcript;
    document.getElementById("condInput").value = text;
    logTerminal(`Transcribed: "<span class="highlight">${text}</span>"`);
    
    // Auto-dispatch if keywords heard
    if(text.toLowerCase().includes("emergency") || text.toLowerCase().includes("help")) {
      logTerminal("Critical keyword detected. Auto-dispatching...");
      setTimeout(handleDispatch, 1000);
    }
  };
  
  rec.onend = () => document.getElementById("btnVoice").classList.remove("recording");
  rec.start();
}

// ==========================================
// 5. HACKER TERMINAL LOGIC
// ==========================================
function logTerminal(msg) {
  const panel = document.getElementById("terminalPanel");
  panel.classList.remove("hidden");
  
  const log = document.getElementById("terminalLog");
  const div = document.createElement("div");
  div.innerHTML = `> ${msg}`;
  log.appendChild(div);
  log.scrollTop = log.scrollHeight; // Auto-scroll
}

function clearTerminal() {
  document.getElementById("terminalLog").innerHTML = "";
}

// ==========================================
// 6. CORE DISPATCH ENGINE
// ==========================================
async function handleDispatch() {
  const loc = document.getElementById("inputStart").value;
  const cond = document.getElementById("condInput").value;
  const overrideHosp = document.getElementById("hospOverride").value;
  
  if (!loc || !cond) {
    logTerminal("ERROR: Location and Condition are required parameters.");
    return;
  }

  const btn = document.getElementById("btnDispatch");
  btn.innerText = "ROUTING..."; 
  btn.disabled = true;
  
  clearTerminal();
  document.getElementById("resultDashboard").classList.add("hidden");
  cleanMap();

  try {
    logTerminal(`Geocoding incident origin: <span class="highlight">${loc}</span>`);
    const startLL = await geocode(loc);
    
    logTerminal(`Transmitting payload to AI Swarm Orchestrator...`);
    
    let apiData;
    try {
      // Try hitting the Flask backend
      const resp = await fetch(BACKEND, {
        method: "POST", 
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({condition: cond, location: loc, lat: startLL[0], lon: startLL[1], override_hospital: overrideHosp})
      });
      if(!resp.ok) throw new Error("Backend HTTP Error");
      apiData = await resp.json();
    } catch (e) {
      logTerminal(`Backend unreachable. Initializing Local Edge-AI Simulation Fallback.`);
      apiData = simulateBackend(cond, startLL[0], startLL[1], overrideHosp); // Fallback for robust demo
    }

    logTerminal(`NLP Triage Agent: Severity classified as <span class="highlight">${apiData.severity.level}</span>`);
    logTerminal(`Hospital Agent: Target locked on ${apiData.hospital.name}.`);
    
    if(apiData.hospital.switched) {
      logTerminal(`CRITICAL ALERT: ${apiData.hospital.switch_reason}`);
    }

    // Communication simulation
    logTerminal(`[COMMUNICATIONS] Transmitting patient condition (${cond}) to ${apiData.hospital.name} ER...`);
    
    const rxFile = document.getElementById("rxFileInput").files[0];
    if (rxFile) {
      logTerminal(`[COMMUNICATIONS] Securely transferring uploaded medical file (${rxFile.name}) to ${apiData.hospital.name} Database...`);
    }

    logTerminal(`[COMMUNICATIONS] Alerting Traffic Police HQ: Clear corridor for incoming ambulance...`);

    // Map Drawing and Animation
    const destLL = [apiData.hospital.lat, apiData.hospital.lon];
    logTerminal(`Routing Agent: Fetching optimized OSRM polyline.`);
    await drawRouteAndAnimate(startLL, destLL, apiData);

    // Update Dashboard UI
    populateDashboard(apiData);
    
    // Announce via Text-To-Speech
    speakBriefing(`Emergency dispatched to ${apiData.hospital.name}. Estimated time of arrival: ${apiData.route.optimized} minutes.`);

  } catch (err) {
    logTerminal(`SYSTEM ERROR: ${err.message}`);
  } finally {
    btn.innerText = "DISPATCH EMERGENCY (Ctrl+Enter)"; 
    btn.disabled = false;
  }
}

// ==========================================
// 7. MAP RENDERING & AMBULANCE ANIMATION
// ==========================================
function cleanMap() {
  if(mapRoute) map.removeLayer(mapRoute);
  if(mapRouteGlow) map.removeLayer(mapRouteGlow);
  if(ambulanceMarker) map.removeLayer(ambulanceMarker);
  markers.forEach(m => map.removeLayer(m));
  trafficLightMarkers.forEach(m => map.removeLayer(m));
  markers = []; 
  trafficLightMarkers = [];
  clearInterval(animInterval);
}

async function drawRouteAndAnimate(startLL, destLL, apiData) {
  // Fetch from real OSRM API
  const url = `https://router.project-osrm.org/route/v1/driving/${startLL[1]},${startLL[0]};${destLL[1]},${destLL[0]}?overview=full&geometries=geojson`;
  const res = await fetch(url);
  const data = await res.json();
  
  if (!data.routes || data.routes.length === 0) {
      throw new Error("No driving route found between these locations. Try a closer location.");
  }
  const geoj = data.routes[0].geometry;
  
  // Calculate Actual Distance and Time
  const distance_km = (data.routes[0].distance / 1000).toFixed(1);
  const duration_min = Math.ceil(data.routes[0].duration / 60);
  
  const isCritical = apiData.severity.level === "CRITICAL";
  
  // Update apiData with real calculated values
  apiData.route.distance = distance_km;
  apiData.route.optimized = duration_min;
  
  // Simulate time saved via AI Traffic Override
  if (isCritical) {
    apiData.route.time_saved = Math.ceil(duration_min * 0.6); 
  } else {
    apiData.route.time_saved = 0;
  }

  const color = isCritical ? "#ef4444" : "#06b6d4";

  // Draw Glowing Route
  mapRouteGlow = L.geoJSON(geoj, {style: {color, weight: 12, opacity: 0.2}}).addTo(map);
  mapRoute = L.geoJSON(geoj, {style: {color, weight: 4, opacity: 0.8, dashArray:"10 10"}}).addTo(map);
   
  map.fitBounds(mapRoute.getBounds(), {padding: [50, 50]});

  markers.push(L.marker(startLL).addTo(map).bindPopup("Incident Origin"));
  markers.push(L.marker(destLL).addTo(map).bindPopup(`<b>${apiData.hospital.name}</b><br>Target Destination<br><br>🛏️ ICU: ${apiData.hospital.icu} | Gen: ${apiData.hospital.gen}`));

  // Plot Alternative Nearby Hospitals
  if (apiData.nearby_hospitals) {
    apiData.nearby_hospitals.forEach(h => {
      if (h.name !== apiData.hospital.name) {
        const marker = L.marker([h.lat, h.lon], {
          icon: L.divIcon({html: '🏥', className:'secondary-hosp-icon', iconSize:[20,20]})
        }).addTo(map).bindPopup(`<b>${h.name}</b><br>Alternative Option`);
        markers.push(marker);
      }
    });
  }

  // IoT Traffic Light Simulation (Hackathon WOW Feature)
  const coords = geoj.coordinates; 
  const numLights = 3;
  
  if (isCritical) {
    logTerminal("Deploying IoT Traffic Node Overrides along route...");
    for(let i=1; i<=numLights; i++) {
      const idx = Math.floor((coords.length / (numLights+1)) * i);
      const ll = [coords[idx][1], coords[idx][0]];
      const tl = L.marker(ll, {
        icon: L.divIcon({html: '🔴', className:'traffic-light', iconSize:[20,20]})
      }).addTo(map);
      tl.visited = false;
      trafficLightMarkers.push({marker: tl, index: idx});
    }
  }

  // Animate Ambulance
  let step = 0;
  const totalSteps = coords.length;
  ambulanceMarker = L.marker([coords[0][1], coords[0][0]], {
    icon: L.divIcon({html: '<div id="amb-emoji" style="transition: transform 0.2s ease;">🚑</div>', className:'ambulance-icon', iconSize:[28,28]})
  }).addTo(map);

  logTerminal(`Commencing real-time ambulance tracking simulation...`);

  animInterval = setInterval(() => {
    if(step >= totalSteps) {
      clearInterval(animInterval);
      logTerminal("Ambulance arrived at destination. Transferring patient.");
      return;
    }
    
    const currentLL = [coords[step][1], coords[step][0]];
    ambulanceMarker.setLatLng(currentLL);
    
    // Face direction based on movement
    if (step > 0) {
      const prevLon = coords[step-1][0];
      const curLon = coords[step][0];
      const emojiEl = document.getElementById("amb-emoji");
      if (emojiEl) {
        if (curLon > prevLon) emojiEl.style.transform = "scaleX(-1)"; 
        else if (curLon < prevLon) emojiEl.style.transform = "scaleX(1)"; 
      }
    }
    
    // Check proximity to IoT Traffic Lights
    if (isCritical) {
      trafficLightMarkers.forEach((tl, i) => {
        if(!tl.visited && step > tl.index - 5) {
          tl.visited = true;
          tl.marker.setIcon(L.divIcon({html: '🟢', className:'traffic-light green', iconSize:[24,24]}));
          logTerminal(`IoT Broadcast: Override Signal #${i+1} to GREEN. Traffic halted.`);
          showSignalAlert(`Overriding Traffic Signal #${i+1} - Green Active`);
        }
      });
    }

    // Step size determines speed.
    step += 1;
  }, 50); 
}

function showSignalAlert(msg) {
  const el = document.getElementById("signalAlert");
  el.querySelector('.text').innerText = msg;
  el.classList.remove("hidden");
  setTimeout(() => el.classList.add("hidden"), 3000);
}

// ==========================================
// 8. UI UPDATES
// ==========================================
function populateDashboard(data) {
  document.getElementById("resultDashboard").classList.remove("hidden");
  
  const sevEl = document.getElementById("rcSev");
  sevEl.innerText = data.severity.level;
  sevEl.style.backgroundColor = data.severity.level === "CRITICAL" ? "#ef4444" : (data.severity.level==="MODERATE" ? "#f59e0b" : "#10b981");
  
  document.getElementById("rcHospName").innerText = data.hospital.name;
  document.getElementById("rcHospAddr").innerText = data.hospital.address;
  document.getElementById("rcIcu").innerText = data.hospital.icu;
  document.getElementById("rcGen").innerText = data.hospital.gen;
  
  const switchEl = document.getElementById("rcSwitchMsg");
  if(data.hospital.switched) {
    switchEl.innerText = data.hospital.switch_reason;
    switchEl.classList.remove("hidden");
  } else {
    switchEl.classList.add("hidden");
  }

  document.getElementById("rcETA").innerText = data.route.optimized;
  document.getElementById("rcDist").innerText = data.route.distance;
  document.getElementById("rcSaved").innerText = data.route.time_saved;
  document.getElementById("rcRouteDesc").innerText = data.route.desc;
  document.getElementById("rcAiSummary").innerText = data.messages.medical_summary;
  document.getElementById("rcTrafficAlert").innerText = data.messages.traffic_alert || "No active traffic alerts.";
  document.getElementById("rcHospitalAlert").innerText = data.messages.hospital_alert || "No active hospital alerts.";
}

function speakBriefing(text) {
  const synth = window.speechSynthesis;
  if(synth) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.05;
    utterance.pitch = 0.9; 
    synth.speak(utterance);
  }
}

// ==========================================
// 9. LOCAL SIMULATION (FALLBACK ENGINE)
// ==========================================
function simulateBackend(condition, userLat, userLon, overrideHosp) {
  // Local Haversine
  function calcDist(lat1, lon1, lat2, lon2) {
    const R = 6371; 
    const dLat = (lat2-lat1)*Math.PI/180;
    const dLon = (lon2-lon1)*Math.PI/180;
    const a = Math.sin(dLat/2) * Math.sin(dLat/2) + Math.cos(lat1*Math.PI/180) * Math.cos(lat2*Math.PI/180) * Math.sin(dLon/2) * Math.sin(dLon/2);
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  }

  const c = condition.toLowerCase();
  const sev = (c.includes("heart") || c.includes("attack") || c.includes("stroke") || c.includes("accident") || c.includes("unconscious")) ? "CRITICAL" : "MODERATE";
  
  const HOSP_DB = [
    {name: "Apollo Gleneagles", icu:0, gen:45, addr:"58, Canal Circular Rd, Kadapara, Phoolbagan, Kankurgachi, Kolkata, West Bengal 700054", lat:22.5748, lon:88.4016},
    {name: "SSKM Medical", icu:15, gen:80, addr:"SSKM Hospital Rd, Bhowanipore, Kolkata, West Bengal 700020", lat:22.5399, lon:88.3417},
    {name: "Barrackpore City Hospital", icu:5, gen:20, addr:"Hospital, 165, Ghosh Para Rd, Barrackpore, Kolkata, West Bengal 700120", lat:22.7680, lon:88.3580},
    {name: "Fortis Hospital", icu:8, gen:60, addr:"730, Eastern Metropolitan Bypass, Anandapur, East Kolkata Twp, Kolkata, West Bengal 700107", lat:22.5186, lon:88.4067},
    {name: "BM Birla Heart", icu:12, gen:30, addr:"1, 1, National Library Ave, Alipore, Kolkata, West Bengal 700027", lat:22.5327, lon:88.3283},
    {name: "Dr B N Bose Sub Divisional Hospital", icu:10, gen:50, addr:"Q92C+M9V, Barrackpore Trunk Rd, Barrackpore, West Bengal 700123", lat:22.7515, lon:88.3710}
  ];

  if (userLat && userLon) {
    HOSP_DB.sort((a,b) => calcDist(userLat, userLon, a.lat, a.lon) - calcDist(userLat, userLon, b.lat, b.lon));
  }

  let best_hospital = HOSP_DB[0];
  let switched = false;
  let switch_reason = "";
  
  if (overrideHosp) {
    const forced = HOSP_DB.find(h => h.name === overrideHosp);
    if (forced) best_hospital = forced;
  } else {
    if(sev === "CRITICAL" && best_hospital.icu === 0) {
      const orig_name = best_hospital.name;
      const icu_hospitals = HOSP_DB.filter(h => h.icu > 0);
      if(icu_hospitals.length > 0) {
          best_hospital = icu_hospitals[0];
          switched = true;
          switch_reason = `⚠️ AI OVERRIDE: ICU FULL at ${orig_name} — Auto-diverted to nearest available: ${best_hospital.name}`;
      }
    }
  }

  let trafficDesc = sev === "CRITICAL" ? "Traffic Control Notified → Police clearing route" : "Standard Fastlane Routing";
  
  let medSummary = `Edge AI Summary: Patient presents with ${condition}. Vital signs unconfirmed. Prepare emergency bay and specialist consult.`;
  let trafficAlert = sev === "CRITICAL" ? "High Priority: Overriding all traffic signals along route to ensure uninterrupted path." : "Normal traffic rules apply.";
  let hospAlert = sev === "CRITICAL" ? `Urgent: Reserve ICU bed at ${best_hospital.name}. Trauma team standby.` : "Patient inbound. General admission prep.";

  return {
    severity: {level: sev},
    hospital: { ...best_hospital, switched, switch_reason },
    nearby_hospitals: HOSP_DB.slice(0,4),
    route: { 
      optimized: sev==="CRITICAL"?12:18, 
      time_saved: 13, 
      desc: trafficDesc 
    },
    messages: { 
      medical_summary: medSummary,
      traffic_alert: trafficAlert,
      hospital_alert: hospAlert
    }
  };
}

// Init Console
console.log("%cClearRoute AI Network Initialized", "color:#06b6d4; font-size: 20px; font-weight: bold;");