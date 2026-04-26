from __future__ import annotations

MAIN_JS = r"""
import * as THREE from "three";
import { OrbitControls } from "./vendor/OrbitControls.js";
import { VRButton } from "./vendor/VRButton.js";
import { GLTFLoader } from "./vendor/GLTFLoader.local.js";

const canvas = document.getElementById("c");
const panel = document.getElementById("panel");
const panelTitle = document.getElementById("panelTitle");
const panelBody = document.getElementById("panelBody");
const panelHint = document.getElementById("panelHint");
const backBtn = document.getElementById("backBtn");
const predictBtn = document.getElementById("predictBtn");
const applyBtn = document.getElementById("applyBtn");
const panelBadge = document.getElementById("panelBadge");
const agentBubble = document.getElementById("agentBubble");
const agentBtn = document.getElementById("agentBtn");
const agentBackBtn = document.getElementById("agentBackBtn");
const envOverlay = document.getElementById("envOverlay");
const envOverlayClose = document.getElementById("envOverlayClose");
const envOverlayCity = document.getElementById("envOverlayCity");
const envOverlayGrid = document.getElementById("envOverlayGrid");
const envOverlayInsight = document.getElementById("envOverlayInsight");
const envOverlayForecast = null;
const overview = document.querySelector(".overview");
const hud = document.getElementById("hud");
const errorBox = document.getElementById("errorBox");

function showError(msg) {
  errorBox.textContent = msg;
  errorBox.classList.remove("hidden");
}

function showAgentBubble(title, body, tone = "neutral") {
  if (!agentBubble) return;
  // Pollutant composition overlay uses the same corner; never stack the agent bubble on top.
  if (envDrilldown) return;
  agentBubble.classList.remove("hidden", "toneGreen", "toneYellow", "toneRed", "toneNeutral");
  agentBubble.classList.add(tone === "green" ? "toneGreen" : tone === "yellow" ? "toneYellow" : tone === "red" ? "toneRed" : "toneNeutral");
  agentBubble.querySelector(".bubbleTitle").textContent = title || "AI Agent";
  agentBubble.querySelector(".bubbleBody").textContent = body || "";
}

function hideAgentBubble() {
  agentBubble?.classList?.add("hidden");
}

// Keep it as an async accessor so the rest of the code doesn't change shape.
const _gltfLoader = new GLTFLoader();
async function getGltfLoader() { return _gltfLoader; }

const REGIONS = {
  shanghai: {
    name: "Shanghai",
    lat: 31.2304,
    lon: 121.4737,
    data: {
      "Monitoring Status": "Critical",
      "Energy Consumption": "18.6 MWh",
      "Carbon Emission": "12.4 tCO2e", // this week
      "Environmental Risk": "High",
      "Equipment Status": "Abnormal",
      "Alert Level": "Red",
      "Main Issue": "Abnormal energy spike detected",
      "AI Prediction": "If current load continues, carbon emission may exceed threshold within 6 hours.",
      "AI Optimization Plan": "Reduce non-critical load, inspect cooling equipment, and shift demand to off-peak hours.",
    },
    carbonWeekly: [9.2, 10.1, 10.8, 11.4, 10.9, 11.7, 12.4, 12.1, 11.6, 12.0, 12.3, 12.4],
    pollutants: {
      "CO₂": { level: 12.4, unit: "tCO2e/w", trend: +1 },
      "PM2.5": { level: 82, unit: "µg/m³", trend: +1 },
      "PM10": { level: 118, unit: "µg/m³", trend: 0 },
      "NOx": { level: 210, unit: "ppb", trend: +1 },
      "SO₂": { level: 52, unit: "ppb", trend: 0 },
      "VOCs": { level: 640, unit: "ppm", trend: +1 },
    },
    aiEnvInsight: "PM2.5 and NOx levels are increasing due to traffic and industrial activity. If trends persist, air quality may degrade within 6 hours.",
  },
  new_york: {
    name: "New York",
    lat: 40.7128,
    lon: -74.006,
    data: {
      "Monitoring Status": "Stable",
      "Energy Consumption": "4.6 MWh",
      "Carbon Emission": "2.2 tCO2e", // this week
      "Environmental Risk": "Low",
      "Equipment Status": "Normal",
      "Alert Level": "Green",
      "Main Issue": "Data quality ready for reporting",
      "AI Prediction": "Current monitoring data is sufficient for automated ESG reporting.",
      "AI Optimization Plan": "Generate carbon ledger and prepare compliance report.",
    },
    carbonWeekly: [2.6, 2.4, 2.3, 2.2, 2.1, 2.0, 2.2, 2.3, 2.1, 2.0, 2.1, 2.2],
    pollutants: {
      "CO₂": { level: 2.2, unit: "tCO2e/w", trend: 0 },
      "PM2.5": { level: 18, unit: "µg/m³", trend: -1 },
      "PM10": { level: 32, unit: "µg/m³", trend: 0 },
      "NOx": { level: 68, unit: "ppb", trend: -1 },
      "SO₂": { level: 14, unit: "ppb", trend: 0 },
      "VOCs": { level: 210, unit: "ppm", trend: 0 },
    },
    aiEnvInsight: "Air quality is stable. CO₂ remains low and particulates are within normal range. Maintain sensor calibration for consistent ESG reporting.",
  },
  london: {
    name: "London",
    lat: 51.5072,
    lon: -0.1276,
    data: {
      "Monitoring Status": "Warning",
      "Energy Consumption": "11.7 MWh",
      "Carbon Emission": "8.2 tCO2e", // this week
      "Environmental Risk": "Medium",
      "Equipment Status": "Warning",
      "Alert Level": "Yellow",
      "Main Issue": "Equipment efficiency decline",
      "AI Prediction": "Efficiency may continue declining if maintenance is delayed.",
      "AI Optimization Plan": "Schedule predictive maintenance and reduce idle equipment time.",
    },
    carbonWeekly: [7.4, 7.6, 7.8, 7.9, 8.0, 7.7, 7.9, 8.1, 8.3, 8.0, 8.1, 8.2],
    pollutants: {
      "CO₂": { level: 8.2, unit: "tCO2e/w", trend: +1 },
      "PM2.5": { level: 41, unit: "µg/m³", trend: +1 },
      "PM10": { level: 62, unit: "µg/m³", trend: 0 },
      "NOx": { level: 128, unit: "ppb", trend: +1 },
      "SO₂": { level: 28, unit: "ppb", trend: 0 },
      "VOCs": { level: 460, unit: "ppm", trend: 0 },
    },
    aiEnvInsight: "PM2.5 and NOx are drifting upward. If maintenance is delayed, efficiency loss may increase emissions and degrade local air quality.",
  },
  dubai: {
    name: "Dubai",
    lat: 25.2048,
    lon: 55.2708,
    data: {
      "Monitoring Status": "Warning",
      "Energy Consumption": "16.5 MWh",
      "Carbon Emission": "10.9 tCO2e", // this week
      "Environmental Risk": "Medium",
      "Equipment Status": "Warning",
      "Alert Level": "Yellow",
      "Main Issue": "Cooling demand increase",
      "AI Prediction": "High temperature may increase energy consumption over the next 8 hours.",
      "AI Optimization Plan": "Optimize HVAC setpoints and pre-cool during lower-load periods.",
    },
    carbonWeekly: [9.1, 9.4, 9.7, 9.9, 10.2, 10.5, 10.6, 10.8, 10.7, 10.8, 10.9, 10.9],
    pollutants: {
      "CO₂": { level: 10.9, unit: "tCO2e/w", trend: +1 },
      "PM2.5": { level: 49, unit: "µg/m³", trend: +1 },
      "PM10": { level: 138, unit: "µg/m³", trend: +1 },
      "NOx": { level: 156, unit: "ppb", trend: 0 },
      "SO₂": { level: 42, unit: "ppb", trend: 0 },
      "VOCs": { level: 520, unit: "ppm", trend: +1 },
    },
    aiEnvInsight: "PM10 is elevated and VOCs are rising with cooling demand. If temperature remains high, energy use and emissions may increase over the next 8 hours.",
  },
  tokyo: {
    name: "Tokyo",
    lat: 35.6762,
    lon: 139.6503,
    data: {
      "Monitoring Status": "Warning",
      "Energy Consumption": "13.2 MWh",
      "Carbon Emission": "7.8 tCO2e", // this week
      "Environmental Risk": "Medium",
      "Equipment Status": "Warning",
      "Alert Level": "Yellow",
      "Main Issue": "Peak-hour load fluctuation",
      "AI Prediction": "Energy demand may rise during evening peak hours.",
      "AI Optimization Plan": "Activate demand response and adjust flexible loads.",
    },
    carbonWeekly: [6.8, 7.0, 7.1, 7.2, 7.4, 7.6, 7.7, 7.5, 7.6, 7.7, 7.8, 7.8],
    pollutants: {
      "CO₂": { level: 7.8, unit: "tCO2e/w", trend: +1 },
      "PM2.5": { level: 34, unit: "µg/m³", trend: 0 },
      "PM10": { level: 58, unit: "µg/m³", trend: 0 },
      "NOx": { level: 122, unit: "ppb", trend: +1 },
      "SO₂": { level: 22, unit: "ppb", trend: 0 },
      "VOCs": { level: 410, unit: "ppm", trend: 0 },
    },
    aiEnvInsight: "NOx shows peak-hour fluctuations. Evening traffic may raise NOx and PM2.5 levels; consider demand response to reduce emissions intensity.",
  },
  singapore: {
    name: "Singapore",
    lat: 1.3521,
    lon: 103.8198,
    data: {
      "Monitoring Status": "Stable",
      "Energy Consumption": "9.8 MWh",
      "Carbon Emission": "5.1 tCO2e", // this week
      "Environmental Risk": "Low",
      "Equipment Status": "Normal",
      "Alert Level": "Green",
      "Main Issue": "Normal operation",
      "AI Prediction": "Energy demand and carbon emission are expected to remain stable for the next 24 hours.",
      "AI Optimization Plan": "Maintain current strategy and continue AIoT monitoring.",
    },
    carbonWeekly: [5.4, 5.3, 5.2, 5.1, 5.0, 5.0, 5.1, 5.2, 5.1, 5.0, 5.1, 5.1],
    pollutants: {
      "CO₂": { level: 5.1, unit: "tCO2e/w", trend: 0 },
      "PM2.5": { level: 22, unit: "µg/m³", trend: 0 },
      "PM10": { level: 36, unit: "µg/m³", trend: 0 },
      "NOx": { level: 74, unit: "ppb", trend: 0 },
      "SO₂": { level: 16, unit: "ppb", trend: 0 },
      "VOCs": { level: 260, unit: "ppm", trend: 0 },
    },
    aiEnvInsight: "All pollutants are within normal range. Maintain current strategy and continue AIoT monitoring to keep carbon intensity stable.",
  },
  sydney: {
    name: "Sydney",
    lat: -33.8688,
    lon: 151.2093,
    data: {
      "Monitoring Status": "Stable",
      "Energy Consumption": "6.3 MWh",
      "Carbon Emission": "1.4 tCO2e", // this week
      "Environmental Risk": "Low",
      "Equipment Status": "Normal",
      "Alert Level": "Green",
      "Main Issue": "Monitoring system stable",
      "AI Prediction": "Local energy-carbon indicators are expected to remain stable today.",
      "AI Optimization Plan": "Continue monitoring and share best practices with higher-risk cities.",
    },
    carbonWeekly: [1.9, 1.8, 1.7, 1.6, 1.5, 1.5, 1.4, 1.5, 1.4, 1.4, 1.4, 1.4],
    pollutants: {
      "CO₂": { level: 1.4, unit: "tCO2e/w", trend: 0 },
      "PM2.5": { level: 16, unit: "µg/m³", trend: -1 },
      "PM10": { level: 28, unit: "µg/m³", trend: 0 },
      "NOx": { level: 52, unit: "ppb", trend: 0 },
      "SO₂": { level: 12, unit: "ppb", trend: 0 },
      "VOCs": { level: 180, unit: "ppm", trend: 0 },
    },
    aiEnvInsight: "Environmental indicators are stable. Low particulates and NOx suggest good air quality; continue monitoring and share best practices with higher-risk cities.",
  },
};

const state = {};
for (const key of Object.keys(REGIONS)) {
  state[key] = {
    alert: REGIONS[key].data["Alert Level"],
    monitoring: REGIONS[key].data["Monitoring Status"],
    equipment: REGIONS[key].data["Equipment Status"],
    carbon: REGIONS[key].data["Carbon Emission"],
    energy: REGIONS[key].data["Energy Consumption"],
    prediction: "",
    plan: "",
  };
}

let selectedKey = null;
let mode = "globe"; // "globe" | "detail" | "agent"

// Local GLB models (provided by you) — no Tripo prompts.
const LOCAL_MODELS = {
  globeIcon: {
    shanghai: "./models/shanghai_oriental_pearl.glb",
    new_york: "./models/nyc_empire_state.glb",
    london: "./models/london_big_ben.glb",
    dubai: "./models/dubai_burj_khalifa.glb",
    tokyo: "./models/tokyo_tower.glb",
    singapore: "./models/singapore_merlion.glb",
    // Country icon near Sydney
    sydney: "./models/australia_kangaroo.glb",
  },
  detailLandmark: {
    shanghai: "./models/shanghai_oriental_pearl.glb",
    new_york: "./models/nyc_empire_state.glb",
    london: "./models/london_big_ben.glb",
    dubai: "./models/dubai_burj_khalifa.glb",
    tokyo: "./models/tokyo_tower.glb",
    singapore: "./models/singapore_merlion.glb",
    sydney: "./models/sydney_opera_house.glb",
  },
};

async function loadTripoAssetsIfPresent() {
  try {
    const res = await fetch("./tripo_assets.json", { cache: "no-store" });
    if (!res.ok) return null;
    const json = await res.json();
    // Supported shapes:
    // 1) { globeIcon: { cityKey: url }, detailLandmark: { cityKey: url } }
    // 2) { assets: { cityKey: { globeIconUrl, detailUrl } } }
    // 3) legacy: { landmark_<cityKey>: { resources: { model | pbr_model } } , ... }
    if (json && (json.globeIcon || json.detailLandmark)) return json;
    if (json && json.assets) {
      const out = { globeIcon: {}, detailLandmark: {} };
      for (const [k, v] of Object.entries(json.assets)) {
        if (v?.globeIconUrl) out.globeIcon[k] = v.globeIconUrl;
        if (v?.detailUrl) out.detailLandmark[k] = v.detailUrl;
      }
      return out;
    }
    if (json && typeof json === "object") {
      const out = { globeIcon: {}, detailLandmark: {} };
      for (const [k, v] of Object.entries(json)) {
        if (!k.startsWith("landmark_")) continue;
        const cityKey = k.replace(/^landmark_/, "");
        const modelUrl = v?.resources?.model || v?.resources?.pbr_model;
        if (modelUrl) {
          out.globeIcon[cityKey] = modelUrl;
          out.detailLandmark[cityKey] = modelUrl;
        }
      }
      if (Object.keys(out.globeIcon).length) return out;
    }
    return null;
  } catch {
    return null;
  }
}

// Scene
const scene = new THREE.Scene();
scene.background = new THREE.Color(0x02040d);
scene.fog = new THREE.FogExp2(0x02040d, 0.035);

const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.01, 200);
camera.position.set(0, 0.55, 4.2);

const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, powerPreference: "high-performance" });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.setSize(window.innerWidth, window.innerHeight);
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.15;
renderer.xr.enabled = true;

try { document.body.appendChild(VRButton.createButton(renderer)); } catch (e) { console.warn("VR button unavailable", e); }

const controls = new OrbitControls(camera, canvas);
controls.enableDamping = true;
controls.dampingFactor = 0.06;
controls.enablePan = false;
controls.minDistance = 2.3;
controls.maxDistance = 7;
controls.rotateSpeed = 0.55;
let userInteracting = false;
controls.addEventListener("start", () => userInteracting = true);
controls.addEventListener("end", () => userInteracting = false);

// lighting
scene.add(new THREE.AmbientLight(0x80dfff, 0.55));
const keyLight = new THREE.DirectionalLight(0xc7f6ff, 2.1);
keyLight.position.set(3, 2.5, 3);
scene.add(keyLight);
const rimLight = new THREE.DirectionalLight(0x2cffdd, 1.2);
rimLight.position.set(-3, 1.5, -2);
scene.add(rimLight);
scene.add(createStars());

// NeuroAgent mini avatar (HUD-ish) for globe home.
const neuroHud = new THREE.Group();
neuroHud.visible = false;
camera.add(neuroHud);
scene.add(camera);
loadNeuroAgentHud().catch(() => {});
let neuroHudOpen = false;

const neuroStage = new THREE.Group();
neuroStage.visible = false;
scene.add(neuroStage);

function enterAgentView() {
  mode = "agent";
  selectedKey = null;
  envDrilldown = false;
  setEnvOverlayVisible(false);
  hideAgentBubble();
  globeGroup.visible = false;
  detailGroup.visible = false;
  neuroStage.visible = true;
  neuroHudOpen = false;
  if (agentBtn) agentBtn.classList.remove("isOpen");
  hud?.classList?.add("hidden");
  overview?.classList?.add("hidden");
  panel?.classList?.add("hidden");
  if (backBtn) backBtn.classList.add("hidden");
  agentBackBtn?.classList?.remove("hidden");
  // Camera framing for agent stage
  camera.position.set(0.0, 0.65, 2.6);
  controls.minDistance = 1.4;
  controls.maxDistance = 6.5;
  controls.rotateSpeed = 0.6;
  controls.target.set(0, 0.55, 0);
  controls.update();
}

function exitAgentView() {
  mode = "globe";
  globeGroup.visible = true;
  detailGroup.visible = false;
  neuroStage.visible = false;
  hud?.classList?.remove("hidden");
  overview?.classList?.remove("hidden");
  panel?.classList?.add("hidden");
  agentBackBtn?.classList?.add("hidden");
  // Restore globe camera constraints
  camera.position.set(0, 0.55, 4.2);
  controls.minDistance = 2.3;
  controls.maxDistance = 7;
  controls.rotateSpeed = 0.55;
  controls.target.set(0, 0.3, 0);
  controls.update();
}

agentBtn?.addEventListener("click", () => {
  if (mode === "agent") return;
  enterAgentView();
});
agentBackBtn?.addEventListener("click", () => {
  if (mode !== "agent") return;
  exitAgentView();
});

async function loadNeuroAgentHud() {
  try {
    const loader = await getGltfLoader();
    const gltf = await loader.loadAsync("./models/neuro_agent.glb");
    const root = gltf.scene || gltf.scenes?.[0];
    if (!root) return;
    normalizeModel(root, 0.24);
    root.traverse((o) => {
      if (!o?.isMesh) return;
      const m = o.material;
      // Keep original colors/materials. Only add a subtle emissive boost if the material already supports it.
      if (m && "emissiveIntensity" in m) {
        try { m.emissiveIntensity = Math.max(Number(m.emissiveIntensity || 0), 0.18); } catch {}
      }
      try { o.frustumCulled = false; } catch {}
    });
    neuroHud.add(root);

    // Larger clone for the dedicated agent view.
    const stageRoot = root.clone(true);
    normalizeModel(stageRoot, 1.5);
    stageRoot.position.set(0, 0, 0);
    neuroStage.add(stageRoot);
    neuroStage.userData.root = stageRoot;
  } catch (e) {
    console.warn("[NeuroAgent] failed to load", e);
  }
}

// Globe
const globeGroup = new THREE.Group();
scene.add(globeGroup);
const R = 1.35;

// Earth meshes live in their own group so we can rotate the texture/orientation
// without moving marker positions.
const earthGroup = new THREE.Group();
globeGroup.add(earthGroup);
// Texture alignment tweak (degrees). Adjust if your Earth texture is rotated.
// Fine-tune this if labels feel globally shifted.
// Note: on this texture/camera setup, increasing this value visually shifts labels WEST.
const EARTH_Y_ROTATION_DEG = 268;
earthGroup.rotation.y = THREE.MathUtils.degToRad(EARTH_Y_ROTATION_DEG);

const earthBase = new THREE.Mesh(
  new THREE.SphereGeometry(R, 96, 96),
  new THREE.MeshStandardMaterial({ color: 0x0d3768, roughness: 0.75, metalness: 0.08, emissive: 0x071a2d, emissiveIntensity: 0.55 })
);
earthGroup.add(earthBase);

const wire = new THREE.Mesh(
  new THREE.SphereGeometry(R * 1.004, 64, 64),
  new THREE.MeshBasicMaterial({ color: 0x32e8ff, wireframe: true, transparent: true, opacity: 0.085 })
);
earthGroup.add(wire);

const atmosphere = new THREE.Mesh(
  new THREE.SphereGeometry(R * 1.045, 64, 64),
  new THREE.MeshBasicMaterial({ color: 0x2cffdd, transparent: true, opacity: 0.13, side: THREE.BackSide, blending: THREE.AdditiveBlending, depthWrite: false })
);
earthGroup.add(atmosphere);

// Heatmap overlay (CanvasTexture on a thin sphere)
const heatmap = createGlobeHeatmapOverlay(R * 1.012);
earthGroup.add(heatmap.mesh);

loadEarthTextureAsync();
function loadEarthTextureAsync() {
  const loader = new THREE.TextureLoader();
  loader.load("./textures/earth_atmos_2048.jpg", (tex) => {
    tex.colorSpace = THREE.SRGBColorSpace;
    earthBase.material.map = tex;
    earthBase.material.color.set(0xffffff);
    earthBase.material.needsUpdate = true;
  }, undefined, () => {});

  loader.load("./textures/earth_normal_2048.jpg", (tex) => {
    earthBase.material.normalMap = tex;
    earthBase.material.needsUpdate = true;
  }, undefined, () => {});
}

function createGlobeHeatmapOverlay(radius) {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 512;
  const ctx = canvas.getContext("2d");

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.wrapS = THREE.RepeatWrapping;
  tex.wrapT = THREE.ClampToEdgeWrapping;

  const mat = new THREE.MeshBasicMaterial({
    map: tex,
    transparent: true,
    opacity: 0.55,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const mesh = new THREE.Mesh(new THREE.SphereGeometry(radius, 96, 96), mat);

  function alertStrength(alert) {
    const r = alertToRank(alert);
    return r === 2 ? 1.0 : r === 1 ? 0.62 : 0.30;
  }

  function strengthColor(s) {
    // value -> color ramp (green->yellow->red)
    const c1 = new THREE.Color(0x46ffa6);
    const c2 = new THREE.Color(0xffd26a);
    const c3 = new THREE.Color(0xff3b5a);
    const c = s < 0.5 ? c1.clone().lerp(c2, s / 0.5) : c2.clone().lerp(c3, (s - 0.5) / 0.5);
    return `rgba(${Math.round(c.r * 255)},${Math.round(c.g * 255)},${Math.round(c.b * 255)},`;
  }

  function lonLatToUv(lon, lat) {
    // lon: -180..180, lat: -90..90
    const u = (lon + 180) / 360;
    const v = 1 - (lat + 90) / 180;
    return { u, v };
  }

  function drawBlob(x, y, radiusPx, rgbaPrefix, a) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, radiusPx);
    g.addColorStop(0.0, `${rgbaPrefix}${Math.min(0.9, a)})`);
    g.addColorStop(0.45, `${rgbaPrefix}${Math.min(0.55, a * 0.75)})`);
    g.addColorStop(1.0, `${rgbaPrefix}0)`);
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, radiusPx, 0, Math.PI * 2);
    ctx.fill();
  }

  function redraw(tSec = 0) {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // subtle scanline/wave base
    ctx.save();
    ctx.globalAlpha = 0.14;
    ctx.strokeStyle = "rgba(120,240,255,0.10)";
    for (let y = 0; y < canvas.height; y += 26) {
      ctx.beginPath();
      const wob = 8 * Math.sin(tSec * 0.7 + y * 0.05);
      ctx.moveTo(0, y + wob);
      ctx.lineTo(canvas.width, y - wob);
      ctx.stroke();
    }
    ctx.restore();

    ctx.save();
    ctx.globalCompositeOperation = "lighter";

    for (const [k, region] of Object.entries(REGIONS)) {
      const alert = state[k]?.alert || region.data["Alert Level"];
      const s = alertStrength(alert);
      const rgbaPrefix = strengthColor(s);

      const { u, v } = lonLatToUv(region.lon, region.lat);
      const x = u * canvas.width;
      const y = v * canvas.height;

      // radius and intensity: scale with strength + a little breathing
      const breathe = 0.85 + 0.15 * Math.sin(tSec * 1.3 + (k.length * 1.7));
      // Smaller hotspot footprint (tuned for readability).
      const r0 = (18 + 30 * s) * breathe;
      const a0 = (0.28 + 0.48 * s) * breathe;

      // main blob
      drawBlob(x, y, r0, rgbaPrefix, a0);

      // wrap around seam for blobs near edges
      if (x < r0) drawBlob(x + canvas.width, y, r0, rgbaPrefix, a0);
      if (x > canvas.width - r0) drawBlob(x - canvas.width, y, r0, rgbaPrefix, a0);
    }

    ctx.restore();
    tex.needsUpdate = true;
  }

  redraw(0);

  const overlay = {
    mesh,
    redraw,
  };
  mesh.userData.tick = (t) => {
    // light animation + periodic redraw
    mat.opacity = 0.42 + 0.18 * (0.5 + 0.5 * Math.sin(t * 0.6));
    if (!overlay._lastRedraw || (t - overlay._lastRedraw) > 0.12) {
      overlay._lastRedraw = t;
      redraw(t);
    }
  };

  return overlay;
}

// City markers + labels
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
const clickableObjects = [];
const markerObjects = {};
const labelObjects = {};

for (const [key, region] of Object.entries(REGIONS)) {
  const pos = latLonToVector(region.lat, region.lon, R * 1.015);
  const color = alertColor(state[key]?.alert || region.data["Alert Level"]);
  const marker = createMarker(color);
  marker.position.copy(pos);
  marker.lookAt(new THREE.Vector3(0, 0, 0));
  marker.userData.key = key;
  globeGroup.add(marker);
  markerObjects[key] = marker;

  const label = createLabel(region.name, color, false);
  label.position.copy(pos.clone().multiplyScalar(1.18));
  label.userData.key = key;
  globeGroup.add(label);
  labelObjects[key] = label;

  const hit = new THREE.Mesh(new THREE.SphereGeometry(0.11, 18, 18), new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.001, depthWrite: false }));
  hit.position.copy(label.position);
  hit.userData.key = key;
  globeGroup.add(hit);
  clickableObjects.push(hit);
}

// Load small landmark "icons" on the globe for supported cities.
loadLocalGlobeIcons().catch(() => {});

async function loadLocalGlobeIcons() {
  const tripo = await loadTripoAssetsIfPresent();
  // Prefer local packaged models for key cities; remote URLs are fallback.
  const globeMap = tripo?.globeIcon ? { ...tripo.globeIcon, ...LOCAL_MODELS.globeIcon } : LOCAL_MODELS.globeIcon;
  for (const [key, url] of Object.entries(globeMap)) {
    const region = REGIONS[key];
    if (!region) continue;
    try {
      const loader = await getGltfLoader();
      const gltf = await loader.loadAsync(url);
      const root = gltf.scene || gltf.scenes?.[0];
      if (!root) continue;
      normalizeModel(root, 0.22);
      const c = alertColor(state[key]?.alert || region.data["Alert Level"]);
      root.traverse((o) => {
        if (!o?.isMesh) return;
        const m = o.material;
        if (m && "emissive" in m) {
          try {
            m.emissive = m.emissive || new THREE.Color(0x000000);
            m.emissive.setHex(c);
            m.emissiveIntensity = 0.18;
          } catch {}
        }
      });
      const pos = latLonToVector(region.lat, region.lon, R * 1.07);
      root.position.copy(pos);
      // Stand it up on the globe: align model +Y with surface normal.
      const normal = pos.clone().normalize();
      root.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), normal);
      // Optional: add a small twist so fronts aren't random (keeps consistency).
      root.rotateOnAxis(normal, THREE.MathUtils.degToRad(18));
      globeGroup.add(root);
    } catch (e) {
      console.warn("[GLB icon] failed", key, url, e);
    }
  }
}

canvas.addEventListener("pointermove", (e) => {
  const rect = canvas.getBoundingClientRect();
  pointer.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
  pointer.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
});
canvas.addEventListener("click", () => {
  if (mode !== "globe") return;
  raycaster.setFromCamera(pointer, camera);
  const hits = raycaster.intersectObjects(clickableObjects, false);
  if (hits.length) enterDetail(hits[0].object.userData.key);
});

// Detail view scene (city landmark + KPI visuals)
const detailGroup = new THREE.Group();
detailGroup.visible = false;
scene.add(detailGroup);

let landmark = null;
let kpiViz = null;
let carbonTrend = null;
let envDrilldown = false;
let draggingLandmark = false;
let draggingCarbonTrend = false;
let detailLandmarkLoadToken = 0;
const detailLandmarkCache = new Map(); // key -> THREE.Object3D
const detailLandmarkInFlight = new Map(); // key -> Promise<THREE.Object3D|null>
const dragTmp = new THREE.Vector3();
const dragStartNdc = new THREE.Vector2();
let dragStartNdcZ = 0;
const dragStartWorld = new THREE.Vector3();
const dragStartPos = new THREE.Vector3();
const DRAG_SENSITIVITY = 0.65;     // < 1 => less jumpy
const DRAG_MAX_RADIUS = 1.05;      // keep landmark near center stage
const DRAG_MAX_Z = 0.25;           // prevent sliding under the right-side panel/bubble
const CARBON_DRAG_MAX_RADIUS = 1.38;
const CARBON_DRAG_MAX_Z = 0.36;

canvas.addEventListener("pointerdown", () => {
  if (mode !== "detail") return;
  raycaster.setFromCamera(pointer, camera);
  const dragPlane = carbonTrend?.visible ? carbonTrend.getObjectByName("carbonDragPlane") : null;
  let hitCarbon = null;
  if (dragPlane) {
    const ch = raycaster.intersectObject(dragPlane, false);
    if (ch.length) hitCarbon = ch[0];
  }
  let hitLand = null;
  if (landmark) {
    const lh = raycaster.intersectObject(landmark, true);
    if (lh.length) hitLand = lh[0];
  }
  if (!hitCarbon && !hitLand) return;
  const pickCarbon = hitCarbon && (!hitLand || hitCarbon.distance <= hitLand.distance);
  if (pickCarbon) {
    draggingCarbonTrend = true;
    draggingLandmark = false;
    dragStartPos.set(carbonTrend.userData.dragX, 0, carbonTrend.userData.dragZ);
    dragStartNdc.copy(pointer);
    dragStartNdcZ = carbonTrend.position.clone().project(camera).z;
    dragStartWorld.set(pointer.x, pointer.y, dragStartNdcZ).unproject(camera);
    controls.enabled = false;
    return;
  }
  draggingLandmark = true;
  draggingCarbonTrend = false;
  dragStartPos.copy(landmark.position);
  dragStartNdc.copy(pointer);
  dragStartNdcZ = landmark.position.clone().project(camera).z;
  dragStartWorld.set(pointer.x, pointer.y, dragStartNdcZ).unproject(camera);
  controls.enabled = false;
});

window.addEventListener("pointerup", () => {
  if (!draggingLandmark && !draggingCarbonTrend) return;
  draggingLandmark = false;
  draggingCarbonTrend = false;
  controls.enabled = true;
});

canvas.addEventListener("pointermove", () => {
  if (mode !== "detail") return;
  if (draggingCarbonTrend && carbonTrend) {
    dragTmp.set(pointer.x, pointer.y, dragStartNdcZ).unproject(camera);
    const dx = (dragTmp.x - dragStartWorld.x) * DRAG_SENSITIVITY;
    const dz = (dragTmp.z - dragStartWorld.z) * DRAG_SENSITIVITY;
    carbonTrend.userData.dragX = dragStartPos.x + dx;
    carbonTrend.userData.dragZ = dragStartPos.z + dz;
    const r = Math.hypot(carbonTrend.userData.dragX, carbonTrend.userData.dragZ);
    if (r > CARBON_DRAG_MAX_RADIUS) {
      const s = CARBON_DRAG_MAX_RADIUS / (r || 1);
      carbonTrend.userData.dragX *= s;
      carbonTrend.userData.dragZ *= s;
    }
    carbonTrend.userData.dragZ = Math.min(CARBON_DRAG_MAX_Z, carbonTrend.userData.dragZ);
    return;
  }
  if (!draggingLandmark || !landmark) return;
  dragTmp.set(pointer.x, pointer.y, dragStartNdcZ).unproject(camera);
  const dx = (dragTmp.x - dragStartWorld.x) * DRAG_SENSITIVITY;
  const dz = (dragTmp.z - dragStartWorld.z) * DRAG_SENSITIVITY;
  landmark.position.set(dragStartPos.x + dx, 0, dragStartPos.z + dz);

  // Clamp to a safe stage area (prevents "running away" + going under UI).
  const r = Math.hypot(landmark.position.x, landmark.position.z);
  if (r > DRAG_MAX_RADIUS) {
    const s = DRAG_MAX_RADIUS / (r || 1);
    landmark.position.x *= s;
    landmark.position.z *= s;
  }
  landmark.position.z = Math.min(DRAG_MAX_Z, landmark.position.z);
});

function clamp01(x) { return Math.max(0, Math.min(1, x)); }

function parseNumber(s) {
  const m = String(s ?? "").match(/-?\d+(\.\d+)?/);
  return m ? Number(m[0]) : 0;
}

function alertToRank(alert) {
  const a = String(alert || "").toLowerCase();
  if (a === "red" || a === "critical") return 2;
  if (a === "yellow" || a === "warning") return 1;
  return 0;
}

function rankToAlert(rank) {
  if (rank >= 2) return "Red";
  if (rank === 1) return "Yellow";
  return "Green";
}

function alertColor(alert) {
  const r = alertToRank(alert);
  if (r === 2) return 0xff3b5a;
  if (r === 1) return 0xffd26a;
  return 0x46ffa6;
}

function alertClass(alert) {
  const r = alertToRank(alert);
  if (r === 2) return "alertRed";
  if (r === 1) return "alertYellow";
  return "alertGreen";
}

function pollutantStatusFor(name, level) {
  // Demo thresholds (hackathon-friendly, visually meaningful).
  switch (name) {
    case "CO₂":       return level >= 11 ? "High" : level >= 7 ? "Warning" : "Normal"; // tCO2e weekly proxy
    case "PM2.5":     return level >= 75 ? "High" : level >= 35 ? "Warning" : "Normal"; // µg/m³
    case "PM10":      return level >= 130 ? "High" : level >= 60 ? "Warning" : "Normal"; // µg/m³
    case "NOx":       return level >= 220 ? "High" : level >= 120 ? "Warning" : "Normal"; // ppb proxy
    case "SO₂":       return level >= 80 ? "High" : level >= 35 ? "Warning" : "Normal"; // ppb proxy
    case "VOCs":      return level >= 900 ? "High" : level >= 450 ? "Warning" : "Normal"; // ppm proxy
    default:          return "Normal";
  }
}

function statusToRank(s) {
  const v = String(s || "").toLowerCase();
  if (v === "high" || v === "critical" || v === "poor") return 2;
  if (v === "warning" || v === "moderate") return 1;
  return 0;
}

function envStatusColor(status) {
  const r = statusToRank(status);
  if (r === 2) return { hex: 0xff3b5a, cls: "envPoor", label: "POOR" };
  if (r === 1) return { hex: 0xffd26a, cls: "envModerate", label: "MODERATE" };
  return { hex: 0x46ffa6, cls: "envGood", label: "GOOD" };
}

function computeEnvironmentalAssessment(key) {
  const region = REGIONS[key];
  const s = state[key] || {};
  const d = region.data;
  const pollutants = region.pollutants || {};

  let high = 0, warn = 0;
  let penalty = 0;

  for (const [name, p] of Object.entries(pollutants)) {
    const level = Number(p.level ?? 0);
    const st = pollutantStatusFor(name, level);
    const r = statusToRank(st);
    if (r === 2) high++;
    if (r === 1) warn++;
    penalty += r === 2 ? 18 : r === 1 ? 7 : 0;
  }

  // carbon + equipment signals
  const co2 = parseNumber(s.carbon || d["Carbon Emission"]);
  if (co2 >= 11) penalty += 12;
  else if (co2 >= 7) penalty += 6;

  const eq = String(s.equipment || d["Equipment Status"] || "").toLowerCase();
  if (eq.includes("abnormal")) penalty += 16;
  else if (eq.includes("warning")) penalty += 8;

  const index = Math.max(0, Math.min(100, Math.round(100 - penalty)));

  let status = "Good";
  if (high >= 1) status = "Poor";
  else if (warn >= 2 || warn >= 1 && penalty > 18) status = "Moderate";

  return { index, status };
}

function computeMonitoringHealth(key) {
  const s = state[key] || {};
  const a = alertToRank(s.alert);
  const energy = parseNumber(s.energy);
  const carbon = parseNumber(s.carbon);
  // simple demo heuristic: lower alert + lower carbon intensity => higher health
  const carbonPenalty = clamp01((carbon - 2.0) / 12.0) * 22;
  const energyPenalty = clamp01((energy - 4.0) / 18.0) * 10;
  const alertPenalty = a === 2 ? 40 : a === 1 ? 18 : 6;
  return Math.max(0, Math.min(100, Math.round(100 - alertPenalty - carbonPenalty - energyPenalty)));
}

function enterDetail(key) {
  selectedKey = key;
  mode = "detail";
  detailLandmarkLoadToken++;

  neuroStage.visible = false;
  hud?.classList?.remove("hidden");
  agentBackBtn?.classList?.add("hidden");

  globeGroup.visible = false;
  detailGroup.visible = true;
  overview?.classList?.add("hidden");
  controls.enabled = true;
  controls.enablePan = false;
  controls.minDistance = 1.6;
  controls.maxDistance = 6.5;
  controls.rotateSpeed = 0.6;

  if (backBtn) backBtn.classList.remove("hidden");
  panel.classList.remove("hidden");
  panelTitle.textContent = REGIONS[key].name;
  panelHint.textContent = "Generate AI prediction, then apply optimization to reduce risk.";
  predictBtn?.removeAttribute("disabled");
  applyBtn?.removeAttribute("disabled");
  showAgentBubble(
    `${REGIONS[key].name} · Local AI Agent`,
    "Click “Generate AI Prediction” to get a risk forecast and optimization plan.",
    alertToRank(state[key]?.alert) === 2 ? "red" : alertToRank(state[key]?.alert) === 1 ? "yellow" : "green"
  );

  // rebuild 3D content
  detailGroup.clear();
  const score = computeMonitoringHealth(key);
  const c = alertColor(state[key]?.alert);
  // Landmark: try Tripo/local GLB; show a loader placeholder first.
  landmark = createLoadingPlaceholder(c);
  detailGroup.add(landmark);
  loadLocalDetailLandmarkInto(key, detailGroup, landmark).catch(() => {});
  // Removed KPI bars + ring by request.
  kpiViz = null;
  carbonTrend = createCarbonTrendViz(key, c);
  detailGroup.add(carbonTrend);
  envDrilldown = false;
  setEnvOverlayVisible(false);
  renderEnvOverlay(key);

  // camera framing
  camera.position.set(0.0, 0.55, 3.2);
  controls.target.set(0, 0.6, 0);
  controls.update();

  const sk = state[key];
  sk.prediction = "";
  sk.plan = "";
  renderPanelBody(key, score);
}

function exitDetail() {
  mode = "globe";
  selectedKey = null;
  globeGroup.visible = true;
  detailGroup.visible = false;
  neuroStage.visible = false;
  hud?.classList?.remove("hidden");
  agentBackBtn?.classList?.add("hidden");
  overview?.classList?.remove("hidden");
  controls.enabled = true;
  if (backBtn) backBtn.classList.add("hidden");
  panel.classList.add("hidden");
  draggingLandmark = false;
  draggingCarbonTrend = false;
  hideAgentBubble();
  carbonTrend = null;
  envDrilldown = false;
  setEnvOverlayVisible(false);
}

backBtn?.addEventListener("click", exitDetail);
predictBtn?.addEventListener("click", () => {
  if (mode !== "detail" || !selectedKey) return;
  predictBtn.disabled = true;
  generateAiPrediction(selectedKey).finally(() => predictBtn.disabled = false);
});
applyBtn?.addEventListener("click", () => {
  if (mode !== "detail" || !selectedKey) return;
  applyOptimization(selectedKey);
});
window.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && mode === "detail") exitDetail();
  if (e.key === "Escape" && mode === "agent") exitAgentView();
});

// Click ENVIRONMENTAL STATUS card to toggle pollutant drilldown.
panelBody?.addEventListener("click", (e) => {
  if (mode !== "detail" || !selectedKey) return;
  const el = e.target?.closest?.(".envRow");
  if (!el) return;
  toggleEnvDrilldown();
});

function toggleEnvDrilldown() {
  envDrilldown = !envDrilldown;
  if (landmark) landmark.visible = !envDrilldown;
  if (carbonTrend) carbonTrend.visible = !envDrilldown;
  if (envDrilldown) {
    hideAgentBubble();
    if (selectedKey) renderEnvOverlay(selectedKey);
    setEnvOverlayVisible(true);
    panelHint.textContent =
      "Environmental drilldown: pollutant composition + AI insight. Click ENVIRONMENTAL STATUS again to return.";
  } else {
    setEnvOverlayVisible(false);
    panelHint.textContent = "Generate AI prediction, then apply optimization to reduce risk.";
    if (mode === "detail" && selectedKey) {
      const rk = alertToRank(state[selectedKey]?.alert);
      showAgentBubble(
        `${REGIONS[selectedKey].name} · Local AI Agent`,
        "Click “Generate AI Prediction” to get a risk forecast and optimization plan.",
        rk === 2 ? "red" : rk === 1 ? "yellow" : "green"
      );
    }
  }
}

envOverlayClose?.addEventListener("click", () => {
  if (mode !== "detail") return;
  if (!envDrilldown) return;
  toggleEnvDrilldown();
});

function setEnvOverlayVisible(v) {
  if (!envOverlay) return;
  if (v) envOverlay.classList.remove("hidden");
  else envOverlay.classList.add("hidden");
}

function hexColor(rgbInt) {
  const h = new THREE.Color(rgbInt).getHex();
  return "#" + h.toString(16).padStart(6, "0");
}

function pollutantBadgeText(status) {
  const v = String(status || "").toLowerCase();
  if (v === "high" || v === "critical" || v === "poor") return "HIGH";
  if (v === "warning" || v === "moderate") return "WARN";
  return "OK";
}

function pollutantBadgeClass(status) {
  const r = statusToRank(status);
  if (r === 2) return "envBadge envBadge--high";
  if (r === 1) return "envBadge envBadge--warn";
  return "envBadge envBadge--ok";
}

function buildPollutantSparklineSvg(level, trend, rgbInt, gradId) {
  const n = 14;
  const pts = [];
  let v = Math.max(0.0001, Number(level));
  const dir = trend > 0 ? 1 : trend < 0 ? -1 : 0;
  const step = v * 0.034 * (dir === 0 ? 0.12 : 1);
  for (let i = 0; i < n; i++) {
    const wobble = Math.sin(i * 0.9) * v * 0.016;
    pts.push(v);
    v = Math.max(0.0001, v + dir * step + wobble * 0.35);
  }
  const lo = Math.min(...pts);
  const hi = Math.max(...pts, lo + 1e-9);
  const W = 128;
  const H = 34;
  const padX = 2;
  const padY = 3;
  const x0 = padX;
  const x1 = W - padX;
  const y0 = padY;
  const y1 = H - padY;
  const pathD = pts
    .map((val, i) => {
      const x = x0 + (i / (n - 1)) * (x1 - x0);
      const t = (val - lo) / (hi - lo);
      const y = y1 - t * (y1 - y0);
      return `${i === 0 ? "M" : "L"}${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
  const strokeHex = hexColor(rgbInt);
  const fillPath = `${pathD} L ${x1} ${y1} L ${x0} ${y1} Z`;
  return `<svg class="envSparklineSvg" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none" aria-hidden="true">
    <defs>
      <linearGradient id="${gradId}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="${strokeHex}" stop-opacity="0.32"/>
        <stop offset="100%" stop-color="${strokeHex}" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <rect class="envSparkGrid" x="0.5" y="0.5" width="${W - 1}" height="${H - 1}" rx="5" />
    <path d="${fillPath}" fill="url(#${gradId})" class="envSparkArea" />
    <path d="${pathD}" fill="none" stroke="${strokeHex}" stroke-width="1.35" stroke-linecap="round" stroke-linejoin="round" class="envSparkStroke" />
  </svg>`;
}

function pollutantHoloFillPct(name, level, status) {
  const caps = {
    "CO₂": 14,
    "PM2.5": 120,
    "PM10": 160,
    "NOx": 260,
    "SO₂": 120,
    "VOCs": 900,
  };
  const cap = caps[name] || 1;
  let pct = (level / cap) * 100;
  const r = statusToRank(status);
  if (r === 2) pct = Math.max(pct, 76);
  else if (r === 1) pct = Math.max(Math.min(pct * 1.04, 90), 34);
  else pct = Math.min(pct * 0.86, 42);
  return Math.round(Math.max(8, Math.min(100, pct)));
}

function renderEnvOverlay(key) {
  if (!envOverlay) return;
  const region = REGIONS[key];
  if (envOverlayCity) envOverlayCity.textContent = `${region.name} · Pollutant Composition`;
  if (envOverlayInsight) envOverlayInsight.textContent = region.aiEnvInsight || "";
  if (envOverlayGrid) {
    envOverlayGrid.innerHTML = "";
    const names = ["CO₂", "PM2.5", "PM10", "NOx", "SO₂", "VOCs"];
    for (let i = 0; i < names.length; i++) {
      const name = names[i];
      const p = region.pollutants?.[name] || { level: 0, unit: "", trend: 0 };
      const level = Number(p.level ?? 0);
      const status = pollutantStatusFor(name, level);
      const rank = statusToRank(status);
      const col = rank === 2 ? 0xff3b5a : rank === 1 ? 0xffd26a : 0x46ffa6;
      const hPct = pollutantHoloFillPct(name, level, status);
      const badgeCls = pollutantBadgeClass(status);
      const badgeTxt = pollutantBadgeText(status);
      const gradId = `envSparkGrad-${i}`;
      const sparkSvg = buildPollutantSparklineSvg(level, Number(p.trend || 0), col, gradId);
      const cCore = rgbaHex(col, 0.98);
      const cGlow = rgbaHex(col, 0.45);
      const cDim = rgbaHex(col, 0.22);
      const tile = document.createElement("div");
      tile.className = "envTile envTile--holo";
      tile.innerHTML = `
        <div class="envTileTop">
          <div class="envTileName">${escapeHtml(name)}</div>
          <span class="${badgeCls}">${escapeHtml(badgeTxt)}</span>
        </div>
        <div class="envTileValRow">
          <span class="envTileVal">${escapeHtml(String(level))}<span class="envTileUnit">${escapeHtml(p.unit || "")}</span></span>
        </div>
        <div class="holoTube" aria-hidden="true">
          <div class="holoTubePedestal"></div>
          <div class="holoTubeGlass" style="--cGlow:${cGlow};">
            <div class="holoTubeInnerGrid"></div>
            <div class="holoLiquidTrack">
              <div class="holoLiquidCore" style="--c:${cCore};--cGlow:${cGlow};--cDim:${cDim};height:${hPct}%;">
                <div class="holoLiquidSheen"></div>
                <div class="holoMeniscus"></div>
              </div>
            </div>
            <div class="holoTubeRim holoTubeRimTop"></div>
            <div class="holoTubeRim holoTubeRimBottom"></div>
            <div class="holoBloomBottom"></div>
          </div>
          <div class="holoParticles">
            <span class="holoParticle" style="--x:18%;--d:0s"></span>
            <span class="holoParticle" style="--x:38%;--d:0.35s"></span>
            <span class="holoParticle" style="--x:52%;--d:0.8s"></span>
            <span class="holoParticle" style="--x:68%;--d:1.15s"></span>
            <span class="holoParticle" style="--x:28%;--d:1.55s"></span>
            <span class="holoParticle" style="--x:78%;--d:2s"></span>
          </div>
        </div>
        <div class="envSparklineWrap">${sparkSvg}</div>
      `;
      envOverlayGrid.appendChild(tile);
    }
  }
}

// UI
function renderPanelBody(key, score) {
  const region = REGIONS[key];
  const s = state[key];
  const d = region.data;
  const env = computeEnvironmentalAssessment(key);
  const envUi = envStatusColor(env.status);
  const badgeCls = alertClass(s.alert);
  const badgeText = String(s.alert || d["Alert Level"] || "Green").toUpperCase();
  if (panelBadge) {
    panelBadge.className = `badge ${badgeCls}`;
    panelBadge.textContent = badgeText;
  }
  panelBody.innerHTML = `
    <div class="kv wide statusRow">
      <div>
        <div class="k">Monitoring Status</div>
        <div class="v">${escapeHtml(String(s.monitoring || d["Monitoring Status"]))}</div>
      </div>
      <div class="badge ${badgeCls}">${escapeHtml(badgeText)}</div>
    </div>
    <div class="kv wide envRow ${envUi.cls}">
      <div class="envLeft">
        <div class="k">ENVIRONMENTAL STATUS</div>
        <div class="envValue">${envUi.label}</div>
        <div class="envSub">AI-computed environmental health score</div>
      </div>
      <div class="envGauge" style="--p:${env.index}; --c:${rgbaHex(envUi.hex,0.95)}">
        <div class="envGaugeInner">
          <div class="envGaugeNum">${env.index}</div>
          <div class="envGaugeDen">/100</div>
        </div>
      </div>
    </div>
    ${kv("Environmental Index", `${env.index} / 100`, "envIndex", false)}
    ${kv("Energy Consumption", s.energy || d["Energy Consumption"])}
    ${kv("Environmental Risk", d["Environmental Risk"])}
    ${kv("Equipment Status", s.equipment || d["Equipment Status"])}
    ${kv("Alert Level", s.alert || d["Alert Level"], badgeCls)}
    ${kv("Main Issue", d["Main Issue"], "", true)}
  `;
}

function kv(k, v, cls = "", wide = false) {
  return `
    <div class="kv ${wide ? "wide" : ""}">
      <div class="k">${escapeHtml(String(k))}</div>
      <div class="v ${cls}">${escapeHtml(String(v))}</div>
    </div>
  `;
}

async function generateAiPrediction(key) {
  const region = REGIONS[key];
  const s = state[key];
  panelHint.textContent = "AI prediction generated (mock). Apply optimization to evaluate risk reduction.";
  s.prediction = region.data["AI Prediction"];
  s.plan = region.data["AI Optimization Plan"];
  showAgentBubble(
    "AI Prediction",
    `Prediction: ${s.prediction}\n\nOptimization: ${s.plan}`,
    alertToRank(s.alert) === 2 ? "red" : alertToRank(s.alert) === 1 ? "yellow" : "green"
  );
}

function applyOptimization(key) {
  const region = REGIONS[key];
  const s = state[key];
  // NOTE: Do not change landmark/agent color or city state here.
  // This button only shows a suggested remediation plan and a projected level-up.
  const currentAlert = (s.alert || region.data["Alert Level"] || "").trim();
  const before = alertToRank(currentAlert);

  if (before <= 0) {
    panelHint.textContent = "Already stable. Optimization suggestion available for efficiency gains.";
    if (!s.plan) s.plan = region.data["AI Optimization Plan"];
    showAgentBubble(
      "Optimization suggestion",
      "Status is already Green / Stable.\nSuggested next step: maintain monitoring cadence, and run weekly anomaly drills to keep carbon intensity flat.",
      "green"
    );
    return;
  }

  const projected = rankToAlert(before - 1);
  if (!s.plan) s.plan = region.data["AI Optimization Plan"];
  const suggestion = s.plan || region.data["AI Optimization Plan"];
  panelHint.textContent = "Optimization suggestion generated. (No state changes applied.)";
  showAgentBubble(
    "Optimization suggestion",
    `If remediation is applied, projected alert: ${currentAlert.toUpperCase()} → ${projected.toUpperCase()}\n\nRecommended actions:\n${suggestion}`,
    before === 2 ? "red" : "yellow"
  );
}

function updateNodeVisuals(key) {
  const alert = state[key]?.alert || REGIONS[key]?.data?.["Alert Level"];
  const c = alertColor(alert);
  const marker = markerObjects[key];
  if (marker) marker.userData.baseColor = c;
  const label = labelObjects[key];
  if (label) updateLabel(label, REGIONS[key].name, c, key === selectedKey);
  if (mode === "detail" && selectedKey === key) {
    // update placeholder glow if GLB still loading
    landmark?.traverse?.((o) => {
      if (o?.material?.emissive) o.material.emissive.setHex(c);
    });
  }
}

function updateOverview() {
  const keys = Object.keys(REGIONS);
  const totalEnergy = keys.reduce((sum, k) => sum + parseNumber(state[k]?.energy || REGIONS[k].data["Energy Consumption"]), 0);
  const totalCarbon = keys.reduce((sum, k) => sum + parseNumber(state[k]?.carbon || REGIONS[k].data["Carbon Emission"]), 0);
  const stable = keys.filter((k) => alertToRank(state[k]?.alert || REGIONS[k].data["Alert Level"]) === 0).length;
  const warningCritical = keys.length - stable;
  const avgHealth = Math.round(keys.reduce((sum, k) => sum + computeMonitoringHealth(k), 0) / keys.length);
  document.getElementById("ovEnergy").textContent = `${totalEnergy.toFixed(1)} MWh`;
  document.getElementById("ovCarbon").textContent = `${totalCarbon.toFixed(1)} tCO2e`;
  document.getElementById("ovStable").textContent = String(stable);
  document.getElementById("ovRisk").textContent = String(warningCritical);
  document.getElementById("ovHealth").textContent = `${avgHealth} / 100`;
}

function createMarker(color) {
  const group = new THREE.Group();
  const dotMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.96 });
  const dot = new THREE.Mesh(new THREE.SphereGeometry(0.018, 16, 16), dotMat);
  group.add(dot);
  const ringMat = new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.28, blending: THREE.AdditiveBlending, side: THREE.DoubleSide, depthWrite: false });
  const ring = new THREE.Mesh(new THREE.RingGeometry(0.02, 0.055, 44), ringMat);
  ring.rotation.x = Math.PI / 2;
  group.add(ring);

  const base = new THREE.Color(color);
  const st = { selected: false };
  group.userData.baseColor = color;
  group.userData.animate = (t) => {
    const pulse = 0.62 + 0.38 * Math.sin(t * 2.0 + group.position.length() * 2.7);
    const isSel = st.selected;
    ringMat.opacity = isSel ? 0.8 : 0.16 + 0.22 * pulse;
    dotMat.opacity = isSel ? 1.0 : 0.78 + 0.14 * pulse;
    const c = new THREE.Color(group.userData.baseColor ?? base);
    dotMat.color.copy(c);
    ringMat.color.copy(c);
    group.scale.setScalar(isSel ? 1.18 : 1.0);
  };
  Object.defineProperty(group.userData, "selected", { get: () => st.selected, set: (v) => st.selected = !!v });
  return group;
}

function createLabel(text, color, selected) {
  const { tex, w } = buildLabelTexture(text, color, selected);
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false });
  const sprite = new THREE.Sprite(mat);
  sprite.scale.set(0.62 * (w / 220), 0.16, 1);
  return sprite;
}

function updateLabel(sprite, text, color, selected) {
  const mat = sprite.material;
  const oldMap = mat.map;
  const { tex, w } = buildLabelTexture(text, color, selected);
  mat.map = tex;
  mat.needsUpdate = true;
  oldMap?.dispose?.();
  sprite.scale.set(0.62 * (w / 220), 0.16, 1);
}

function buildLabelTexture(text, color, selected) {
  const c = document.createElement("canvas");
  const ctx = c.getContext("2d");
  const padding = 12;
  const fontSize = 22;
  ctx.font = `700 ${fontSize}px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto`;
  const w = Math.ceil(ctx.measureText(text).width + padding * 2);
  const h = 54;
  c.width = w;
  c.height = h;
  ctx.clearRect(0, 0, w, h);
  ctx.fillStyle = selected ? "rgba(12,22,40,0.72)" : "rgba(10,16,30,0.55)";
  roundRect(ctx, 0, 0, w, h, 14);
  ctx.fill();
  ctx.strokeStyle = selected ? "rgba(120,240,255,0.55)" : "rgba(120,240,255,0.18)";
  ctx.lineWidth = selected ? 3 : 2;
  roundRect(ctx, 1, 1, w - 2, h - 2, 14);
  ctx.stroke();
  ctx.fillStyle = rgbaHex(color, 0.9);
  ctx.beginPath();
  ctx.arc(18, h / 2, 6, 0, Math.PI * 2);
  ctx.fill();
  ctx.fillStyle = "rgba(230,255,255,0.95)";
  ctx.textBaseline = "middle";
  ctx.fillText(text, 34, h / 2);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.needsUpdate = true;
  return { tex, w };
}

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function rgbaHex(hex, a) {
  const c = new THREE.Color(hex);
  return `rgba(${Math.round(c.r * 255)},${Math.round(c.g * 255)},${Math.round(c.b * 255)},${a})`;
}

// Back-compat alias
function riskColor(x) { return alertColor(x); }

function latLonToVector(latDeg, lonDeg, radius) {
  // Stable marker mapping: lon=0 at +Z, lon=90E at +X, y-up.
  const lat = THREE.MathUtils.degToRad(latDeg);
  const lon = THREE.MathUtils.degToRad(lonDeg);
  const x = radius * Math.cos(lat) * Math.sin(lon);
  const y = radius * Math.sin(lat);
  const z = radius * Math.cos(lat) * Math.cos(lon);
  return new THREE.Vector3(x, y, z);
}

function normalizeModel(obj, targetSize) {
  const box = new THREE.Box3().setFromObject(obj);
  const size = new THREE.Vector3();
  box.getSize(size);
  const maxDim = Math.max(size.x, size.y, size.z) || 1;
  obj.scale.setScalar(targetSize / maxDim);
  const box2 = new THREE.Box3().setFromObject(obj);
  const center = new THREE.Vector3();
  box2.getCenter(center);
  obj.position.sub(center);
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function createStars() {
  function layer({ count, rMin, rMax, size, opacity, color }) {
    const positions = new Float32Array(count * 3);
    const twinkle = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      const r = rMin + Math.random() * (rMax - rMin);
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      positions[i * 3 + 0] = r * Math.sin(phi) * Math.cos(theta);
      positions[i * 3 + 1] = r * Math.cos(phi);
      positions[i * 3 + 2] = r * Math.sin(phi) * Math.sin(theta);
      twinkle[i] = Math.random() * Math.PI * 2;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    geo.setAttribute("twinkle", new THREE.BufferAttribute(twinkle, 1));
    const mat = new THREE.PointsMaterial({
      size,
      color,
      transparent: true,
      opacity,
      sizeAttenuation: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      fog: false,
    });
    const pts = new THREE.Points(geo, mat);
    pts.userData.baseOpacity = opacity;
    pts.userData.tick = (t) => {
      // Slightly stronger twinkle to read on dark backgrounds.
      mat.opacity = pts.userData.baseOpacity * (0.72 + 0.28 * Math.sin(t * 0.75 + 1.3));
    };
    return pts;
  }

  const g = new THREE.Group();
  // Big sparse stars (very obvious)
  g.add(layer({ count: 520, rMin: 14, rMax: 75, size: 0.13, opacity: 0.70, color: 0xffffff }));
  // Dense near field
  g.add(layer({ count: 5200, rMin: 18, rMax: 92, size: 0.085, opacity: 0.86, color: 0xe7f7ff }));
  // Fine far field
  g.add(layer({ count: 3200, rMin: 92, rMax: 165, size: 0.055, opacity: 0.66, color: 0xb7e6ff }));
  g.userData.tick = (t) => g.children.forEach((c) => c.userData.tick?.(t));
  return g;
}

updateOverview();

window.addEventListener("resize", () => {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
});

renderer.setAnimationLoop((ms) => {
  const t = ms * 0.001;
  if (!userInteracting) globeGroup.rotation.y += 0.0016;
  // Top-right floating NeuroAgent (camera-attached).
  neuroHud.visible = mode === "globe" && neuroHudOpen;
  if (neuroHud.visible) {
    neuroHud.position.set(0.58, 0.36, -1.35);
    neuroHud.rotation.set(0, 0.55 + 0.18 * Math.sin(t * 0.9), 0);
    const s = 1.0 + 0.06 * Math.sin(t * 1.2);
    neuroHud.scale.setScalar(s);
  }
  if (mode === "agent" && neuroStage.visible && neuroStage.userData.root) {
    neuroStage.rotation.y = 0.18 * Math.sin(t * 0.6);
  }
  scene.children.forEach((o) => o?.userData?.tick?.(t));
  for (const marker of Object.values(markerObjects)) marker.userData.animate?.(t);
  for (const label of Object.values(labelObjects)) label.quaternion.copy(camera.quaternion);
  if (mode === "detail") {
    landmark?.userData?.tick?.(t);
    kpiViz?.userData?.tick?.(t);
    carbonTrend?.userData?.tick?.(t);
    // Anchor agent bubble near landmark (top-right of its bounding box).
    if (agentBubble && !agentBubble.classList.contains("hidden") && landmark) {
      try {
        const box = new THREE.Box3().setFromObject(landmark);
        const p = new THREE.Vector3(box.max.x, box.max.y, box.max.z);
        p.project(camera);
        const x = (p.x * 0.5 + 0.5) * window.innerWidth;
        const y = (-p.y * 0.5 + 0.5) * window.innerHeight;
        agentBubble.style.transform = `translate(${Math.round(x + 16)}px, ${Math.round(y - 10)}px)`;
      } catch {}
    }
  }
  controls.update();
  renderer.render(scene, camera);
});

function createLoadingPlaceholder(color) {
  const g = new THREE.Group();
  const ring = new THREE.Mesh(
    new THREE.RingGeometry(0.55, 0.9, 80),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.35, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false })
  );
  ring.rotation.x = Math.PI / 2;
  ring.position.y = 0.03;
  g.add(ring);

  const core = new THREE.Mesh(
    new THREE.CylinderGeometry(0.06, 0.06, 0.28, 18),
    new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.22 })
  );
  core.position.y = 0.14;
  g.add(core);

  g.userData.tick = (t) => {
    ring.rotation.z = t * 0.8;
    ring.material.opacity = 0.22 + 0.18 * (0.5 + 0.5 * Math.sin(t * 2.2));
  };
  return g;
}

async function loadLocalDetailLandmarkInto(key, parent, fallback) {
  const token = detailLandmarkLoadToken;
  try {
    const tripo = await loadTripoAssetsIfPresent();
    // Prefer local packaged models for key cities; remote URLs are fallback.
    const detailMap = tripo?.detailLandmark ? { ...tripo.detailLandmark, ...LOCAL_MODELS.detailLandmark } : LOCAL_MODELS.detailLandmark;
    const url = detailMap[key];
    if (!url) return;

    panelHint.textContent = "Loading 3D landmark… (you can still drag the placeholder)";
    const cached = detailLandmarkCache.get(key);
    let root = null;
    if (cached) {
      root = cached.clone(true);
    } else {
      let p = detailLandmarkInFlight.get(key);
      if (!p) {
        p = (async () => {
          const loader = await getGltfLoader();
          const gltf = await loader.loadAsync(url);
          return gltf.scene || gltf.scenes?.[0] || null;
        })();
        detailLandmarkInFlight.set(key, p);
      }
      root = await p;
      detailLandmarkInFlight.delete(key);
      if (root) {
        // Store an original in cache; we clone on use.
        detailLandmarkCache.set(key, root);
        root = root.clone(true);
      }
    }
    if (!root) return;
    // Ignore stale loads (user switched cities).
    if (token !== detailLandmarkLoadToken || selectedKey !== key || mode !== "detail") return;
    normalizeModel(root, 1.9);
    const c = alertColor(state[key]?.alert || REGIONS[key].data["Alert Level"]);
    root.traverse((o) => {
      if (!o?.isMesh) return;
      const m = o.material;
      if (m && "emissive" in m) {
        try {
          m.emissive = m.emissive || new THREE.Color(0x000000);
          m.emissive.setHex(c);
          m.emissiveIntensity = 0.22;
        } catch {}
      }
    });
    root.position.set(0, 0, 0);
    parent.remove(fallback);
    parent.add(root);
    landmark = root;
    panelHint.textContent = "Drag landmark to reposition. Back returns to globe.";
  } catch (e) {
    console.warn("[GLB landmark] failed", key, e);
    if (String(e && e.message ? e.message : e).includes("dynamically imported module")) {
      showError(
        "Failed to load GLTFLoader module.\n\n" +
        "Try hard refresh (Cmd+Shift+R). If it persists, your browser is blocking module imports from this origin."
      );
    }
    showError(
      "Failed to load local GLB landmark.\n\n" +
      `city: ${key}\n` +
      `url: ${url || ""}\n\n` +
      String(e && e.message ? e.message : e)
    );
    panelHint.textContent = "Landmark load failed. Using placeholder.";
  }
}

function createLandmarkFallback(key, color) {
  const group = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color, roughness: 0.35, metalness: 0.25, emissive: new THREE.Color(color).multiplyScalar(0.15) });

  if (key === "shanghai") {
    // Oriental Pearl-ish: spine + spheres
    const spine = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.09, 1.6, 18), mat);
    spine.position.y = 0.8;
    group.add(spine);
    const s1 = new THREE.Mesh(new THREE.SphereGeometry(0.22, 22, 22), mat);
    s1.position.y = 0.45;
    group.add(s1);
    const s2 = new THREE.Mesh(new THREE.SphereGeometry(0.15, 22, 22), mat);
    s2.position.y = 1.1;
    group.add(s2);
    const cap = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.42, 22), mat);
    cap.position.y = 1.55;
    group.add(cap);
  } else if (key === "new_york") {
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.18, 0.9), mat);
    base.position.y = 0.09;
    group.add(base);
    const tower = new THREE.Mesh(new THREE.BoxGeometry(0.38, 1.35, 0.38), mat);
    tower.position.y = 0.85;
    group.add(tower);
    const spire = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 0.35, 12), mat);
    spire.position.y = 1.7;
    group.add(spire);
  } else if (key === "dubai") {
    const geo = new THREE.CylinderGeometry(0.10, 0.28, 1.9, 16);
    const tower = new THREE.Mesh(geo, mat);
    tower.position.y = 0.95;
    group.add(tower);
    const needle = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.02, 0.5, 10), mat);
    needle.position.y = 2.05;
    group.add(needle);
  } else if (key === "london") {
    const base = new THREE.Mesh(new THREE.BoxGeometry(0.55, 1.2, 0.4), mat);
    base.position.y = 0.6;
    group.add(base);
    const top = new THREE.Mesh(new THREE.BoxGeometry(0.45, 0.35, 0.35), mat);
    top.position.y = 1.35;
    group.add(top);
    const crown = new THREE.Mesh(new THREE.ConeGeometry(0.25, 0.35, 16), mat);
    crown.position.y = 1.7;
    group.add(crown);
  } else if (key === "tokyo") {
    const base = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.28, 0.4, 16), mat);
    base.position.y = 0.2;
    group.add(base);
    const tower = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.18, 1.35, 16), mat);
    tower.position.y = 0.95;
    group.add(tower);
    const antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.015, 0.015, 0.55, 10), mat);
    antenna.position.y = 1.75;
    group.add(antenna);
  } else if (key === "singapore") {
    const p1 = new THREE.Mesh(new THREE.BoxGeometry(0.25, 1.0, 0.25), mat);
    const p2 = new THREE.Mesh(new THREE.BoxGeometry(0.25, 1.2, 0.25), mat);
    const p3 = new THREE.Mesh(new THREE.BoxGeometry(0.25, 0.9, 0.25), mat);
    p1.position.set(-0.22, 0.5, 0);
    p2.position.set(0, 0.6, 0);
    p3.position.set(0.22, 0.45, 0);
    group.add(p1, p2, p3);
    const deck = new THREE.Mesh(new THREE.BoxGeometry(0.9, 0.08, 0.3), mat);
    deck.position.set(0, 1.25, 0);
    group.add(deck);
  } else if (key === "sydney") {
    // Kangaroo-ish: body + head + legs + tail (simple but clearly 3D)
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.42, 22, 22), mat);
    body.scale.set(1.25, 0.95, 0.85);
    body.position.set(0.0, 0.55, 0.0);
    group.add(body);

    const head = new THREE.Mesh(new THREE.SphereGeometry(0.18, 20, 20), mat);
    head.scale.set(1.0, 0.9, 0.9);
    head.position.set(0.42, 0.78, 0.02);
    group.add(head);

    const snout = new THREE.Mesh(new THREE.SphereGeometry(0.12, 18, 18), mat);
    snout.scale.set(1.2, 0.65, 0.65);
    snout.position.set(0.55, 0.72, 0.02);
    group.add(snout);

    const earGeo = new THREE.ConeGeometry(0.06, 0.18, 14);
    const ear1 = new THREE.Mesh(earGeo, mat);
    ear1.position.set(0.40, 0.98, 0.09);
    ear1.rotation.z = -0.35;
    ear1.rotation.x = 0.25;
    group.add(ear1);
    const ear2 = ear1.clone();
    ear2.position.z = -0.09;
    ear2.rotation.x = -0.25;
    group.add(ear2);

    const legGeo = new THREE.CylinderGeometry(0.06, 0.08, 0.45, 14);
    const thighGeo = new THREE.CylinderGeometry(0.09, 0.12, 0.42, 14);
    const footGeo = new THREE.BoxGeometry(0.18, 0.06, 0.10);

    function addLeg(z, x, bend) {
      const thigh = new THREE.Mesh(thighGeo, mat);
      thigh.position.set(x, 0.28, z);
      thigh.rotation.z = bend;
      group.add(thigh);

      const shin = new THREE.Mesh(legGeo, mat);
      shin.position.set(x + 0.10, 0.10, z);
      shin.rotation.z = bend * 0.7;
      group.add(shin);

      const foot = new THREE.Mesh(footGeo, mat);
      foot.position.set(x + 0.20, 0.02, z);
      group.add(foot);
    }
    addLeg(0.16, -0.10, -0.55);
    addLeg(-0.16, -0.10, -0.55);

    const armGeo = new THREE.CylinderGeometry(0.035, 0.05, 0.32, 12);
    const arm1 = new THREE.Mesh(armGeo, mat);
    arm1.position.set(0.18, 0.38, 0.18);
    arm1.rotation.z = 0.65;
    group.add(arm1);
    const arm2 = arm1.clone();
    arm2.position.z = -0.18;
    group.add(arm2);

    const tail = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.03, 0.95, 16), mat);
    tail.position.set(-0.55, 0.35, 0.0);
    tail.rotation.z = -0.85;
    group.add(tail);
  }

  const floor = new THREE.Mesh(new THREE.CylinderGeometry(1.2, 1.2, 0.04, 64), new THREE.MeshBasicMaterial({ color: 0x0b1224, transparent: true, opacity: 0.65 }));
  floor.position.y = 0.02;
  group.add(floor);

  const glow = new THREE.Mesh(new THREE.RingGeometry(0.65, 1.05, 80), new THREE.MeshBasicMaterial({ color, transparent: true, opacity: 0.35, side: THREE.DoubleSide, blending: THREE.AdditiveBlending, depthWrite: false }));
  glow.rotation.x = Math.PI / 2;
  glow.position.y = 0.03;
  group.add(glow);

  group.userData.tick = (t) => { glow.material.opacity = 0.22 + 0.18 * (0.5 + 0.5 * Math.sin(t * 2.0)); };
  group.position.set(0, 0, 0);
  return group;
}

function createKpiViz(key, score, color) {
  // KPI bars + rings were removed by request.
  return new THREE.Group();
}

function pollutantColorByStatus(status) {
  const r = statusToRank(status);
  if (r === 2) return 0xff3b5a;
  if (r === 1) return 0xffd26a;
  return 0x46ffa6;
}

function createPollutantBreakdownViz(key) {
  const g = new THREE.Group();
  const region = REGIONS[key];
  const pollutants = region.pollutants || {};
  const names = ["CO₂", "PM2.5", "PM10", "NOx", "SO₂", "VOCs"];

  // Layout (floating near the city/landmark, sci-fi holo columns)
  const baseX = -0.35;
  const baseY = 0.18;
  const baseZ = -0.95;
  const yaw = -0.05;

  // Glass panel
  const panelW = 1.45;
  const panelH = 0.78;
  const panel = new THREE.Mesh(
    new THREE.PlaneGeometry(panelW, panelH),
    new THREE.MeshBasicMaterial({ color: 0x071225, transparent: true, opacity: 0.26, depthWrite: false })
  );
  panel.position.set(baseX, baseY + panelH * 0.5, baseZ);
  panel.rotation.y = yaw;
  g.add(panel);

  const env = computeEnvironmentalAssessment(key);
  const envUi = envStatusColor(env.status);
  const frame = new THREE.Mesh(
    new THREE.PlaneGeometry(panelW * 1.01, panelH * 1.03),
    new THREE.MeshBasicMaterial({ color: envUi.hex, transparent: true, opacity: 0.10, blending: THREE.AdditiveBlending, depthWrite: false })
  );
  frame.position.copy(panel.position);
  frame.rotation.copy(panel.rotation);
  g.add(frame);

  const title = makeTinyTextSprite("[ VIEW POLLUTANTS ]", envUi.hex);
  title.position.set(baseX - panelW * 0.36, baseY + panelH + 0.07, baseZ);
  title.scale.multiplyScalar(1.05);
  title.rotation.y = yaw;
  g.add(title);

  // Bars
  const bars = [];
  const hits = [];
  const barBaseY = baseY + 0.08;
  const x0 = baseX - 0.62;
  const dx = 0.25;
  const maxH = 0.48;

  for (let i = 0; i < names.length; i++) {
    const name = names[i];
    const p = pollutants[name] || { level: 0, unit: "", trend: 0 };
    const level = Number(p.level ?? 0);
    const status = pollutantStatusFor(name, level);
    const col = pollutantColorByStatus(status);

    // Normalize per pollutant (visual-only)
    const norm = (() => {
      const st = statusToRank(status);
      if (st === 2) return 1.0;
      if (st === 1) return 0.62;
      return 0.32 + 0.18 * Math.min(1, level / 1000);
    })();

    const x = x0 + i * dx;

    const bg = new THREE.Mesh(
      new THREE.BoxGeometry(0.10, maxH, 0.10),
      new THREE.MeshBasicMaterial({ color: 0x0b1a33, transparent: true, opacity: 0.35, depthWrite: false })
    );
    bg.position.set(x, barBaseY + maxH * 0.5, baseZ + 0.03);
    bg.rotation.y = yaw;
    g.add(bg);

    const mat = new THREE.MeshStandardMaterial({
      color: col,
      roughness: 0.35,
      metalness: 0.25,
      emissive: new THREE.Color(col).multiplyScalar(0.65),
      emissiveIntensity: 0.9,
      transparent: true,
      opacity: 0.95,
    });
    const bar = new THREE.Mesh(new THREE.BoxGeometry(0.085, 0.001, 0.085), mat);
    bar.position.set(x, barBaseY, baseZ + 0.03);
    bar.rotation.y = yaw;
    bar.userData.targetH = 0.08 + maxH * Math.max(0.05, Math.min(1, norm));
    bar.userData.name = name;
    bar.userData.level = level;
    bar.userData.unit = p.unit;
    bar.userData.status = status;
    bar.userData.trend = p.trend;
    g.add(bar);
    bars.push(bar);

    const label = makeTinyTextSprite(name, col);
    label.position.set(x, baseY + 0.02, baseZ + 0.04);
    label.scale.set(0.22, 0.06, 1);
    label.rotation.y = yaw;
    g.add(label);

    // Tiny trend arrow (3D)
    const arrow = new THREE.Mesh(
      new THREE.ConeGeometry(0.018, 0.06, 14),
      new THREE.MeshBasicMaterial({ color: p.trend > 0 ? 0xffd26a : p.trend < 0 ? 0x46ffa6 : 0x9bdcff, transparent: true, opacity: 0.7, blending: THREE.AdditiveBlending, depthWrite: false })
    );
    arrow.position.set(x + 0.06, baseY + 0.05, baseZ + 0.03);
    arrow.rotation.z = p.trend > 0 ? Math.PI : 0;
    arrow.rotation.y = yaw;
    g.add(arrow);

    const hit = new THREE.Mesh(
      new THREE.BoxGeometry(0.14, maxH + 0.14, 0.16),
      new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.001, depthWrite: false })
    );
    hit.position.set(x, barBaseY + (maxH + 0.14) * 0.5, baseZ + 0.03);
    hit.rotation.y = yaw;
    hit.userData = { name, level, unit: p.unit, status, trend: p.trend };
    g.add(hit);
    hits.push(hit);
  }

  // AI insight label (in-space)
  const insight = makeTinyTextSprite("AI ENVIRONMENTAL INSIGHT", envUi.hex);
  insight.position.set(baseX - panelW * 0.36, baseY - 0.05, baseZ);
  insight.scale.multiplyScalar(0.95);
  insight.rotation.y = yaw;
  g.add(insight);

  // animation
  const born = performance.now() * 0.001;
  g.userData.tick = (t) => {
    const age = Math.min(1, (t - born) / 0.9);
    const breathe = 0.75 + 0.25 * (0.5 + 0.5 * Math.sin(t * 1.2));
    frame.material.opacity = 0.08 + 0.07 * breathe;
    // bars animate upward sequentially
    for (let i = 0; i < bars.length; i++) {
      const b = bars[i];
      const delay = i * 0.04;
      const a = Math.max(0, Math.min(1, (age - delay) / 0.8));
      const h = (b.userData.targetH || 0.2) * (0.12 + 0.88 * a);
      b.scale.y = h / Math.max(0.001, 1.0); // geo is 1; we're using scale
      // keep base anchored
      b.position.y = barBaseY + (h * 0.5);
      b.material.opacity = 0.72 + 0.23 * breathe;
    }

    // hover tooltip via agent bubble
    if (mode !== "detail") return;
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(hits, false)[0];
    if (hit?.object?.userData) {
      const u = hit.object.userData;
      const trendArrow = u.trend > 0 ? "↑" : u.trend < 0 ? "↓" : "→";
      const tone = statusToRank(u.status) === 2 ? "red" : statusToRank(u.status) === 1 ? "yellow" : "green";
      showAgentBubble(
        "Pollutant detail",
        `${u.name}: ${u.level}${u.unit ? " " + u.unit : ""}\nStatus: ${u.status}\nTrend: ${trendArrow}`,
        tone
      );
    }
  };

  g.position.set(0, 0, 0);
  return g;
}

function createCarbonTrendViz(key, color) {
  const g = new THREE.Group();
  g.userData.dragX = 0;
  g.userData.dragZ = 0;
  const region = REGIONS[key];
  const values = (region?.carbonWeekly || []).slice(-12);
  const n = values.length || 12;
  const series = values.length ? values.slice() : new Array(12).fill(parseNumber(state[key]?.carbon || region?.data?.["Carbon Emission"] || 0));
  // Ensure the latest point matches the city's "this week" carbon value (and thus aligns with the city's status).
  const thisWeekCarbon = parseNumber(state[key]?.carbon || region?.data?.["Carbon Emission"] || series[series.length - 1] || 0);
  series[series.length - 1] = thisWeekCarbon;

  const minV = Math.min(...series);
  const maxV = Math.max(...series);
  const span = Math.max(0.001, maxV - minV);

  // Holo panel placement (floating in space, slightly angled)
  const W = 1.35;
  const H = 0.75;
  const baseX = -1.62;
  const baseY = 0.44;
  const baseZ = -0.28;
  const yaw = 0.22;

  // Risk-tinted accent
  const toneRank = alertToRank(state[key]?.alert || region?.data?.["Alert Level"]);
  const accent = toneRank === 2 ? 0xffb26b : toneRank === 1 ? 0xffe29a : 0xaaf6ff;
  const statusHex = toneRank === 2 ? 0xff3b5a : toneRank === 1 ? 0xffd26a : 0x46ffa6;

  // Deterministic "AI feel" extras
  const last = series[series.length - 1];
  const prev = series[series.length - 2] ?? last;
  const slope = (last - prev) / Math.max(0.001, prev);
  const riskPct = Math.round(Math.max(-18, Math.min(22, slope * 120)));
  const conf = 82 + ((key.length * 7) % 14); // 82..95 deterministic

  // Canvas-based rendering (premium HUD look)
  const canvas = document.createElement("canvas");
  canvas.width = 900;
  canvas.height = 520;
  const ctx = canvas.getContext("2d");
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;

  const panelMat = new THREE.MeshBasicMaterial({
    map: tex,
    transparent: true,
    opacity: 1.0,
    depthWrite: false,
  });
  const panel = new THREE.Mesh(new THREE.PlaneGeometry(W, H), panelMat);
  panel.position.set(baseX + W * 0.5, baseY + H * 0.5, baseZ);
  panel.rotation.y = yaw;
  g.add(panel);

  // Invisible hit surface slightly in front of the chart (for dragging the whole panel).
  const dragMat = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.001, depthWrite: false });
  const dragPlane = new THREE.Mesh(new THREE.PlaneGeometry(W * 1.08, H * 1.1), dragMat);
  dragPlane.name = "carbonDragPlane";
  dragPlane.position.set(0, 0, 0.018);
  panel.add(dragPlane);

  // Glow shell (bloom-ish, cheap)
  const glowMat = new THREE.MeshBasicMaterial({
    color: accent,
    transparent: true,
    opacity: 0.12,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
  });
  const glow = new THREE.Mesh(new THREE.PlaneGeometry(W * 1.03, H * 1.05), glowMat);
  glow.position.copy(panel.position);
  glow.rotation.copy(panel.rotation);
  g.add(glow);

  // Node hit targets in 3D aligned to the plane
  const hitGeo = new THREE.SphereGeometry(0.075, 12, 12);
  const hitMat = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0.001, depthWrite: false });
  const hits = [];
  const u0 = 0.10, u1 = 0.93;
  const v0 = 0.20, v1 = 0.78;
  for (let i = 0; i < n; i++) {
    const t = n === 1 ? 0 : i / (n - 1);
    const v = (series[i] - minV) / span;
    const localX = (t * (u1 - u0) + u0 - 0.5) * W;
    const localY = (v * (v1 - v0) + v0 - 0.5) * H;
    const p = new THREE.Vector3(localX, localY, 0.001);
    p.applyEuler(panel.rotation);
    p.add(panel.position);
    const hit = new THREE.Mesh(hitGeo, hitMat);
    hit.position.copy(p);
    hit.userData = { idx: i, value: series[i], key };
    g.add(hit);
    hits.push(hit);
  }
  g.userData.hitPoints = hits;

  // Render function
  const lerp = (a, b, t) => a + (b - a) * t;
  const colorRamp = (t) => {
    // green -> yellow -> red (used by VALUE intensity)
    const c1 = new THREE.Color(0x46ffa6);
    const c2 = new THREE.Color(0xffd26a);
    const c3 = new THREE.Color(0xff3b5a);
    if (t < 0.5) return c1.clone().lerp(c2, t / 0.5);
    return c2.clone().lerp(c3, (t - 0.5) / 0.5);
  };

  let startT = null;
  let hoverIdx = -1;
  g.userData.tick = (tSec) => {
    // Float + breathing (drag offsets on XZ from userData)
    const floatY = 0.02 * Math.sin(tSec * 1.15);
    g.position.set(g.userData.dragX, floatY, g.userData.dragZ);
    glowMat.opacity = 0.10 + 0.05 * (0.5 + 0.5 * Math.sin(tSec * 1.1));

    if (startT == null) startT = tSec;
    const intro = Math.min(1, (tSec - startT) / 1.15); // line draws in ~1.15s
    const breathe = 0.65 + 0.35 * (0.5 + 0.5 * Math.sin(tSec * 1.4));

    // Hover detection
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(hits, false)[0];
    hoverIdx = hit?.object?.userData?.idx ?? -1;

    // Draw canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const cw = canvas.width, ch = canvas.height;

    // Glass background
    ctx.save();
    ctx.globalAlpha = 1.0;
    ctx.fillStyle = "rgba(6, 14, 30, 0.58)";
    roundRect(ctx, 18, 18, cw - 36, ch - 36, 26);
    ctx.fill();
    // soft border
    ctx.strokeStyle = `rgba(120,240,255,${0.14 + 0.10 * breathe})`;
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.restore();

    // Subtle grid/waveform with parallax drift
    const gridAlpha = 0.10;
    const driftX = 8 * Math.sin(tSec * 0.35);
    const driftY = 6 * Math.cos(tSec * 0.28);
    ctx.save();
    ctx.translate(driftX, driftY);
    ctx.strokeStyle = `rgba(120,240,255,${gridAlpha})`;
    ctx.lineWidth = 1;
    for (let x = 60; x < cw - 40; x += 52) {
      ctx.beginPath();
      ctx.moveTo(x, 70);
      ctx.lineTo(x, ch - 70);
      ctx.stroke();
    }
    for (let y = 80; y < ch - 60; y += 44) {
      ctx.beginPath();
      ctx.moveTo(40, y);
      ctx.lineTo(cw - 40, y);
      ctx.stroke();
    }
    // waveform
    ctx.strokeStyle = `rgba(255,255,255,0.05)`;
    ctx.beginPath();
    for (let x = 48; x <= cw - 48; x += 6) {
      const tt = (x / cw) * Math.PI * 2;
      const y = 270 + 18 * Math.sin(tt * 2 + tSec * 0.8);
      if (x === 48) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.restore();

    // Header label: [ CARBON TREND · 12W ]
    const hdr = "[ CARBON TREND · 12W ]";
    ctx.save();
    ctx.font = "900 22px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto";
    ctx.fillStyle = "rgba(230,255,255,0.92)";
    ctx.globalAlpha = 0.95;
    ctx.fillText(hdr, 56, 70);
    // underline/bracket glow
    ctx.strokeStyle = `rgba(120,240,255,${0.25 + 0.20 * breathe})`;
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(56, 82);
    ctx.lineTo(360, 82);
    ctx.stroke();
    ctx.restore();

    // AI extra info
    const arrow = riskPct >= 0 ? "↑" : "↓";
    const riskStr = `${arrow} ${Math.abs(riskPct)}% risk`;
    ctx.save();
    ctx.font = "800 18px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto";
    const riskTint = riskPct > 6 ? "rgba(255,90,110,0.92)" : riskPct > 0 ? "rgba(255,210,90,0.92)" : "rgba(90,255,170,0.92)";
    ctx.fillStyle = riskTint;
    ctx.fillText(`AI Forecast: ${riskStr}`, 56, 112);
    ctx.fillStyle = "rgba(200,240,255,0.68)";
    ctx.font = "700 16px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto";
    ctx.fillText(`Confidence: ${conf}%`, 56, 136);
    ctx.restore();

    // Chart area bounds
    const left = 70, right = cw - 70;
    const top = 170, bottom = ch - 78;
    const plotW = right - left;
    const plotH = bottom - top;

    // Prepare smoothed spline points
    const points = [];
    for (let i = 0; i < n; i++) {
      const tt = n === 1 ? 0 : i / (n - 1);
      const vv = (series[i] - minV) / span;
      const x = left + tt * plotW;
      const y = bottom - vv * plotH;
      points.push({ x, y, tt, vv, val: series[i] });
    }
    const smooth = (i0, i1, t) => lerp(i0, i1, t);

    // Glow curve (multi-stroke for bloom feel). Color is VALUE-driven:
    // higher carbon => redder; lower => greener.
    const drawCurveValueColored = (alpha, lw) => {
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.lineWidth = lw;
      ctx.lineJoin = "round";
      ctx.lineCap = "round";
      const reveal = Math.min(1, intro * 1.02);
      for (let i = 1; i < points.length; i++) {
        const p0 = points[i - 1];
        const p1 = points[i];
        if (p0.tt > reveal) break;
        const midV = (p0.vv + p1.vv) * 0.5;
        // Value-driven color overall, but force the latest tail to match city alert color.
        const segColor = (i === points.length - 1) ? statusHex : colorRamp(midV).getHex();
        ctx.strokeStyle = rgbaHex(segColor, 1);
        ctx.beginPath();
        ctx.moveTo(p0.x, p0.y);
        // light smoothing by aiming at midpoint
        const mx = (p0.x + p1.x) * 0.5;
        const my = (p0.y + p1.y) * 0.5;
        ctx.quadraticCurveTo(p0.x, p0.y, mx, my);
        ctx.lineTo(p1.x, p1.y);
        ctx.stroke();
      }
      ctx.restore();
    };
    drawCurveValueColored(0.10 + 0.05 * breathe, 18);
    drawCurveValueColored(0.18 + 0.06 * breathe, 10);
    drawCurveValueColored(0.85, 4.5);

    // Animated pulse moving along the curve
    const pulseT = (tSec * 0.28) % 1;
    const pulseIdx = pulseT * (points.length - 1);
    const iA = Math.floor(pulseIdx);
    const iB = Math.min(points.length - 1, iA + 1);
    const f = pulseIdx - iA;
    const px = smooth(points[iA].x, points[iB].x, f);
    const py = smooth(points[iA].y, points[iB].y, f);
    const pv = smooth(points[iA].vv, points[iB].vv, f);
    ctx.save();
    ctx.globalAlpha = 0.9;
    const pc = colorRamp(pv);
    ctx.fillStyle = rgbaHex(pc.getHex(), 0.92);
    ctx.shadowBlur = 18;
    ctx.shadowColor = rgbaHex(pc.getHex(), 0.8);
    ctx.beginPath();
    ctx.arc(px, py, 6.5, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // Nodes: sequential fade-in + halo; hover enlarges
    for (let i = 0; i < points.length; i++) {
      const p = points[i];
      const nodeIntro = Math.min(1, Math.max(0, (intro - p.tt) * 4.2));
      if (nodeIntro <= 0) continue;
      const isHover = i === hoverIdx;
      const baseR = isHover ? 7.2 : 5.2;
      const haloR = isHover ? 16 : 12;
      const alpha = (0.20 + 0.80 * nodeIntro) * (0.85 + 0.15 * breathe);
      // Latest point must match city alert color (Dubai=yellow, etc.)
      const nodeColor = (i === points.length - 1) ? statusHex : colorRamp(p.vv).getHex();

      // halo
      ctx.save();
      ctx.globalAlpha = 0.22 * alpha;
      ctx.fillStyle = rgbaHex(nodeColor, 1);
      ctx.shadowBlur = 26;
      ctx.shadowColor = rgbaHex(nodeColor, 0.75);
      ctx.beginPath();
      ctx.arc(p.x, p.y, haloR, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // core
      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = rgbaHex(nodeColor, 1);
      ctx.shadowBlur = 12;
      ctx.shadowColor = rgbaHex(nodeColor, 0.8);
      ctx.beginPath();
      ctx.arc(p.x, p.y, baseR, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // tooltip inside canvas (when hovered)
      if (isHover) {
        const tip = `W-${(points.length - 1 - i)} · ${p.val.toFixed(1)} tCO2e`;
        ctx.save();
        ctx.font = "800 18px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto";
        const tw = ctx.measureText(tip).width;
        const bx = Math.min(cw - 60 - tw - 24, p.x + 14);
        const by = Math.max(70, p.y - 34);
        ctx.fillStyle = "rgba(6, 14, 30, 0.78)";
        roundRect(ctx, bx, by, tw + 24, 34, 12);
        ctx.fill();
        ctx.strokeStyle = rgbaHex(nodeColor, 0.55);
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.fillStyle = "rgba(235,255,255,0.92)";
        ctx.textBaseline = "middle";
        ctx.fillText(tip, bx + 12, by + 17);
        ctx.restore();
      }
    }

    // Small footer hint
    ctx.save();
    ctx.font = "700 14px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto";
    ctx.fillStyle = "rgba(200,240,255,0.46)";
    ctx.fillText("Drag the chart panel to reposition · Hover nodes for weekly tCO2e · AI pulse = time flow", 56, ch - 44);
    ctx.restore();

    tex.needsUpdate = true;

    // External tooltip (agent bubble) stays available too
    if (hoverIdx >= 0) {
      const val = series[hoverIdx];
      const tone = toneRank === 2 ? "red" : toneRank === 1 ? "yellow" : "green";
      showAgentBubble("Carbon history (weekly)", `Week -${(series.length - 1 - hoverIdx)}: ${val.toFixed(1)} tCO2e`, tone);
    }
  };

  return g;
}

function makeTinyTextSprite(text, color) {
  const c = document.createElement("canvas");
  const ctx = c.getContext("2d");
  const fontSize = 28;
  ctx.font = `900 ${fontSize}px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto`;
  const padX = 16;
  const padY = 10;
  const w = Math.ceil(ctx.measureText(text).width + padX * 2);
  const h = fontSize + padY * 2;
  c.width = w;
  c.height = h;
  ctx.font = `900 ${fontSize}px ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto`;
  ctx.fillStyle = "rgba(7, 18, 37, 0.45)";
  roundRect(ctx, 0, 0, w, h, 14);
  ctx.fill();
  ctx.strokeStyle = rgbaHex(color, 0.55);
  ctx.lineWidth = 3;
  roundRect(ctx, 1.5, 1.5, w - 3, h - 3, 14);
  ctx.stroke();
  ctx.fillStyle = rgbaHex(color, 0.92);
  ctx.textBaseline = "middle";
  ctx.fillText(text, padX, h / 2);
  const tex = new THREE.CanvasTexture(c);
  tex.colorSpace = THREE.SRGBColorSpace;
  const mat = new THREE.SpriteMaterial({ map: tex, transparent: true, depthWrite: false });
  const s = new THREE.Sprite(mat);
  s.scale.set(0.9 * (w / 360), 0.16, 1);
  return s;
}
"""


INDEX_HTML = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Lanchuang Global Monitor VR</title>
  <link rel="stylesheet" href="./style.css?v={{BUILD_ID}}" />
  <script type="importmap">
    {
      "imports": {
        "three": "./vendor/three.module.js"
      }
    }
  </script>
</head>
<body>
  <canvas id="c"></canvas>

  <div id="envOverlay" class="envOverlay envOverlay--premium hidden">
    <div class="envOverlayGridBg" aria-hidden="true"></div>
    <div class="envOverlayGlowFloor" aria-hidden="true"></div>
    <div class="envOverlayTop">
      <div>
        <div id="envOverlayCity" class="envOverlayTitle">Pollutant Composition</div>
        <div class="envOverlaySub">Real-time air & emission monitoring</div>
      </div>
      <button id="envOverlayClose" class="envOverlayClose" aria-label="Close">×</button>
    </div>

    <div id="envOverlayGrid" class="envGrid envGrid--holo"></div>

    <div class="envBottom">
      <div class="envInsightBox envInsightBox--premium">
        <div class="envInsightHead">
          <span class="envInsightGlyph" aria-hidden="true"></span>
          <div class="envInsightTitle">AI Environmental Insight</div>
        </div>
        <div id="envOverlayInsight" class="envInsightText"></div>
      </div>
    </div>
  </div>

  <div id="agentBubble" class="agentBubble hidden">
    <div class="bubbleTitle">AI Agent</div>
    <div class="bubbleBody"></div>
  </div>

  <div class="hud" id="hud">
    <div>
      <div class="title">LANCHUANG GLOBAL MONITOR VR</div>
      <div class="subtitle">AIoT Spatial Monitoring Platform for Global Clients</div>
      <div class="tagline">From passive monitoring to proactive prediction & optimization</div>
    </div>
    <div class="hudRight">
      <button id="agentBtn" class="hudAgentBtn" type="button">AGENT</button>
      <div class="hint">Rotate globe · Click a city to enter detail</div>
    </div>
  </div>

  <button id="agentBackBtn" class="agentBackBtn hidden" type="button">Back</button>

  <div class="overview">
    <div class="boxTitle">GLOBAL OVERVIEW</div>
    <div class="metric"><span>Total Energy Consumption</span><b id="ovEnergy">0.0 MWh</b></div>
    <div class="metric"><span>Total Carbon Emission</span><b id="ovCarbon">0.0 tCO2e</b></div>
    <div class="metric"><span>Stable Cities</span><b id="ovStable">0</b></div>
    <div class="metric"><span>Warning / Critical Cities</span><b id="ovRisk">0</b></div>
    <div class="metric"><span>Overall Monitoring Health</span><b id="ovHealth">0 / 100</b></div>
  </div>

  <div id="panel" class="panel hidden">
    <div class="panelHeader">
      <div>
        <div id="panelTitle" class="panelTitle">Select a region</div>
        <div class="panelSub">City AIoT Monitoring Node · Local AI Agent</div>
      </div>
      <div id="panelBadge" class="badge alertGreen">GREEN</div>
    </div>

    <div id="panelBody" class="panelBody"></div>
    <div id="panelHint" class="panelHint">Click a glowing city marker on the globe.</div>
    <div class="buttons">
      <button id="predictBtn">Generate AI Prediction</button>
      <button id="applyBtn" class="greenBtn">Apply Optimization</button>
      <button id="backBtn" class="greenBtn hidden">Back to Globe</button>
    </div>
  </div>

  <div id="errorBox" class="errorBox hidden"></div>

  <script type="module" src="./main.js?v={{BUILD_ID}}"></script>
</body>
</html>
"""


STYLE_CSS = """
html, body {
  margin: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  background: #02040d;
  color: rgba(235, 250, 255, 0.94);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.agentBubble {
  position: fixed;
  left: 0;
  top: 0;
  z-index: 6;
  width: min(360px, calc(100vw - 40px));
  padding: 12px 12px 10px 12px;
  border-radius: 16px;
  background: rgba(8, 17, 34, 0.72);
  border: 1px solid rgba(91, 230, 255, 0.22);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(14px);
  pointer-events: none;
  transform: translate(-9999px, -9999px);
}
.envOverlay {
  position: fixed;
  left: 22px;
  top: 110px;
  width: min(980px, calc(100vw - 520px));
  z-index: 8;
  padding: 18px 18px 16px;
  border-radius: 22px;
  overflow: hidden;
  background: rgba(4, 12, 26, 0.38);
  border: 1px solid rgba(110, 230, 255, 0.28);
  box-shadow:
    0 0 0 1px rgba(80, 200, 255, 0.12),
    0 0 48px rgba(60, 170, 255, 0.22),
    0 24px 80px rgba(0, 0, 0, 0.55),
    inset 0 1px 0 rgba(255, 255, 255, 0.06),
    inset 0 -40px 90px rgba(0, 40, 90, 0.35);
  backdrop-filter: blur(18px);
}
.envOverlayGridBg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  background-image:
    linear-gradient(rgba(72, 190, 255, 0.045) 1px, transparent 1px),
    linear-gradient(90deg, rgba(72, 190, 255, 0.045) 1px, transparent 1px);
  background-size: 22px 22px;
  opacity: 0.55;
  mask-image: linear-gradient(180deg, rgba(0,0,0,0.55) 0%, rgba(0,0,0,0.95) 55%, rgba(0,0,0,0.35) 100%);
}
.envOverlayGlowFloor {
  position: absolute;
  left: 50%;
  bottom: -42%;
  width: 92%;
  height: 58%;
  z-index: 0;
  transform: translateX(-50%);
  pointer-events: none;
  background: radial-gradient(ellipse at center, rgba(90, 210, 255, 0.26) 0%, rgba(40, 120, 200, 0.08) 42%, transparent 68%);
  filter: blur(2px);
}
.envOverlayTop {
  position: relative;
  z-index: 2;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}
.envOverlayTitle {
  font-weight: 950;
  font-size: 16px;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: rgba(201, 251, 255, 0.96);
  text-shadow: 0 0 24px rgba(100, 220, 255, 0.25);
}
.envOverlaySub { margin-top: 6px; font-size: 12px; opacity: 0.62; }
.envOverlayClose {
  position: relative;
  z-index: 2;
  pointer-events: auto;
  width: 36px;
  height: 36px;
  border-radius: 12px;
  border: 1px solid rgba(110, 230, 255, 0.28);
  background: rgba(4, 10, 23, 0.45);
  color: rgba(235, 250, 255, 0.92);
  font-size: 20px;
  font-weight: 900;
  line-height: 1;
  cursor: pointer;
  box-shadow: 0 0 16px rgba(80, 200, 255, 0.12);
}
.envGrid {
  margin-top: 14px;
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
}
.envGrid--holo {
  position: relative;
  z-index: 2;
  margin-top: 16px;
  gap: 10px;
}
.envTile--holo {
  border-radius: 16px;
  padding: 10px 8px 8px;
  min-height: 252px;
  background: linear-gradient(165deg, rgba(8, 22, 44, 0.62) 0%, rgba(3, 10, 24, 0.72) 100%);
  border: 1px solid rgba(100, 210, 255, 0.2);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.05),
    0 10px 32px rgba(0, 0, 0, 0.4);
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  align-items: stretch;
}
.envTileTop {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 6px;
  min-height: 28px;
}
.envTileName {
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(210, 245, 255, 0.88);
  line-height: 1.2;
  min-width: 0;
  word-break: break-word;
}
.envBadge {
  flex-shrink: 0;
  font-size: 8px;
  font-weight: 950;
  letter-spacing: 0.1em;
  padding: 3px 5px;
  border-radius: 6px;
  line-height: 1;
  white-space: nowrap;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(0, 0, 0, 0.25);
}
.envBadge--ok {
  color: rgba(120, 255, 200, 0.95);
  border-color: rgba(100, 255, 190, 0.35);
  box-shadow: 0 0 12px rgba(70, 255, 166, 0.2);
}
.envBadge--warn {
  color: rgba(255, 220, 140, 0.98);
  border-color: rgba(255, 200, 100, 0.4);
  box-shadow: 0 0 12px rgba(255, 200, 100, 0.18);
}
.envBadge--high {
  color: rgba(255, 150, 160, 0.98);
  border-color: rgba(255, 100, 120, 0.45);
  box-shadow: 0 0 12px rgba(255, 80, 100, 0.22);
}
.envTileValRow {
  margin-top: 4px;
  min-height: 26px;
}
.envTileVal {
  font-size: 17px;
  font-weight: 950;
  letter-spacing: 0.02em;
  line-height: 1.15;
  color: rgba(240, 252, 255, 0.96);
}
.envTileUnit {
  margin-left: 4px;
  font-size: 10px;
  opacity: 0.66;
  font-weight: 800;
  letter-spacing: 0.02em;
}
.holoTube {
  position: relative;
  flex: 1;
  min-height: 128px;
  margin-top: 8px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
}
.holoTubePedestal {
  position: absolute;
  left: 50%;
  bottom: 2px;
  width: 72%;
  height: 10px;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(ellipse at center, rgba(80, 200, 255, 0.22) 0%, transparent 72%);
  pointer-events: none;
}
.holoTubeGlass {
  position: relative;
  width: 52px;
  flex: 1;
  min-height: 118px;
  max-height: 148px;
  margin: 0 auto 6px;
  border-radius: 999px;
  border: 1px solid rgba(140, 230, 255, 0.35);
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.06) 0%,
    rgba(30, 80, 120, 0.18) 45%,
    rgba(0, 0, 0, 0.35) 100%
  );
  box-shadow:
    inset 0 0 0 1px rgba(255, 255, 255, 0.05),
    inset 0 -20px 40px rgba(0, 30, 60, 0.45),
    0 0 20px rgba(80, 200, 255, 0.12);
  overflow: hidden;
}
.holoTubeInnerGrid {
  position: absolute;
  inset: 0;
  opacity: 0.22;
  background-image: repeating-linear-gradient(
    0deg,
    rgba(120, 220, 255, 0.09) 0px,
    rgba(120, 220, 255, 0.09) 1px,
    transparent 1px,
    transparent 9px
  );
  pointer-events: none;
}
.holoLiquidTrack {
  position: absolute;
  left: 5px;
  right: 5px;
  top: 14px;
  bottom: 16px;
}
.holoLiquidCore {
  position: absolute;
  left: 1px;
  right: 1px;
  bottom: 0;
  width: auto;
  border-radius: 999px;
  transform-origin: bottom center;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.42) 0%,
    var(--c) 38%,
    var(--cDim) 100%
  );
  box-shadow:
    inset 2px 0 10px rgba(255, 255, 255, 0.25),
    inset -4px 0 14px rgba(0, 0, 0, 0.45),
    0 0 18px var(--cGlow);
}
.envOverlay:not(.hidden) .holoLiquidCore {
  animation:
    holoLiquidRise 1.05s cubic-bezier(0.16, 1, 0.3, 1) both,
    holoGlowPulse 2.8s ease-in-out 1s infinite;
}
.envTile--holo:nth-child(1) .holoLiquidCore { animation-delay: 0.04s, 1s; }
.envTile--holo:nth-child(2) .holoLiquidCore { animation-delay: 0.1s, 1s; }
.envTile--holo:nth-child(3) .holoLiquidCore { animation-delay: 0.16s, 1s; }
.envTile--holo:nth-child(4) .holoLiquidCore { animation-delay: 0.22s, 1s; }
.envTile--holo:nth-child(5) .holoLiquidCore { animation-delay: 0.28s, 1s; }
.envTile--holo:nth-child(6) .holoLiquidCore { animation-delay: 0.34s, 1s; }
@keyframes holoLiquidRise {
  from {
    transform: scaleY(0.04);
    opacity: 0.25;
    filter: brightness(0.7);
  }
  to {
    transform: scaleY(1);
    opacity: 1;
    filter: brightness(1);
  }
}
@keyframes holoGlowPulse {
  0%,
  100% {
    box-shadow:
      inset 2px 0 10px rgba(255, 255, 255, 0.22),
      inset -4px 0 14px rgba(0, 0, 0, 0.45),
      0 0 14px var(--cGlow);
  }
  50% {
    box-shadow:
      inset 2px 0 12px rgba(255, 255, 255, 0.32),
      inset -4px 0 14px rgba(0, 0, 0, 0.45),
      0 0 26px var(--cGlow);
  }
}
.holoLiquidSheen {
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.35) 0%, transparent 42%, rgba(0, 0, 0, 0.25) 100%);
  pointer-events: none;
  mix-blend-mode: overlay;
}
.holoMeniscus {
  position: absolute;
  left: -2px;
  right: -2px;
  top: -6px;
  height: 11px;
  border-radius: 50%;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.65), var(--c));
  opacity: 0.88;
  pointer-events: none;
  box-shadow: 0 -2px 10px rgba(255, 255, 255, 0.2);
}
.holoTubeRim {
  position: absolute;
  left: 4px;
  right: 4px;
  height: 7px;
  border-radius: 50%;
  border: 1px solid rgba(180, 240, 255, 0.28);
  pointer-events: none;
}
.holoTubeRimTop {
  top: 7px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.12), transparent);
}
.holoTubeRimBottom {
  bottom: 8px;
  background: linear-gradient(0deg, rgba(255, 255, 255, 0.08), transparent);
}
.holoBloomBottom {
  position: absolute;
  left: 50%;
  bottom: 4px;
  width: 70%;
  height: 22px;
  transform: translateX(-50%);
  border-radius: 50%;
  background: radial-gradient(ellipse at center, var(--cGlow) 0%, transparent 70%);
  opacity: 0.55;
  filter: blur(4px);
  pointer-events: none;
}
.holoParticles {
  position: absolute;
  inset: 0;
  pointer-events: none;
  overflow: visible;
}
.holoParticle {
  position: absolute;
  left: var(--x, 50%);
  bottom: 18%;
  width: 3px;
  height: 3px;
  margin-left: -1.5px;
  border-radius: 50%;
  background: rgba(200, 245, 255, 0.95);
  box-shadow: 0 0 10px rgba(160, 230, 255, 0.95);
  animation: holoPartFloat 3.4s ease-in-out var(--d, 0s) infinite;
  opacity: 0;
}
@keyframes holoPartFloat {
  0% {
    transform: translateY(8px) scale(0.5);
    opacity: 0;
  }
  12% {
    opacity: 0.95;
  }
  100% {
    transform: translateY(-92px) scale(1);
    opacity: 0;
  }
}
.envSparklineWrap {
  margin-top: 6px;
  height: 34px;
  width: 100%;
  opacity: 0;
  transform: translateY(4px);
}
.envOverlay:not(.hidden) .envSparklineWrap {
  animation: envSparkIn 0.85s ease 0.42s forwards;
}
@keyframes envSparkIn {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.envSparklineSvg {
  display: block;
  width: 100%;
  height: 34px;
}
.envSparkGrid {
  fill: rgba(80, 200, 255, 0.04);
  stroke: rgba(100, 210, 255, 0.12);
  stroke-width: 1;
}
.envSparkStroke {
  opacity: 0.95;
}
.envBottom {
  position: relative;
  z-index: 2;
  margin-top: 14px;
  display: block;
}
.envInsightBox--premium {
  position: relative;
  border-radius: 16px;
  padding: 12px 14px 12px 16px;
  margin-left: 2px;
  border: 1px solid rgba(100, 210, 255, 0.18);
  border-left: 3px solid rgba(90, 220, 255, 0.85);
  background: linear-gradient(105deg, rgba(6, 18, 38, 0.65) 0%, rgba(4, 12, 28, 0.5) 100%);
  box-shadow:
    inset 0 1px 0 rgba(255, 255, 255, 0.04),
    0 10px 36px rgba(0, 0, 0, 0.35);
}
.envInsightHead {
  display: flex;
  align-items: center;
  gap: 10px;
}
.envInsightGlyph {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: radial-gradient(circle at 32% 28%, rgba(200, 255, 255, 0.95) 0%, rgba(60, 180, 255, 0.35) 45%, rgba(8, 30, 60, 0.95) 100%);
  box-shadow:
    0 0 20px rgba(100, 220, 255, 0.5),
    inset 0 0 14px rgba(255, 255, 255, 0.12);
  animation: envInsightPulse 2.6s ease-in-out infinite;
}
@keyframes envInsightPulse {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 0 18px rgba(100, 220, 255, 0.45), inset 0 0 12px rgba(255, 255, 255, 0.1);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 0 28px rgba(100, 220, 255, 0.65), inset 0 0 16px rgba(255, 255, 255, 0.16);
  }
}
.envInsightTitle {
  font-size: 11px;
  font-weight: 950;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(185, 245, 255, 0.92);
}
.envInsightText {
  margin-top: 10px;
  margin-left: 38px;
  font-size: 12px;
  line-height: 1.45;
  opacity: 0.9;
  color: rgba(225, 245, 255, 0.88);
}
@media (max-width: 1100px) {
  .envInsightText {
    margin-left: 0;
  }
}
.envForecastCanvas { margin-top: 10px; width: 100%; height: 140px; display:block; }
.agentBubble::after {
  content: "";
  position: absolute;
  left: 18px;
  bottom: -8px;
  width: 14px;
  height: 14px;
  background: rgba(8, 17, 34, 0.72);
  border-left: 1px solid rgba(91, 230, 255, 0.22);
  border-bottom: 1px solid rgba(91, 230, 255, 0.22);
  transform: rotate(45deg);
}
.bubbleTitle {
  font-size: 12px;
  font-weight: 950;
  letter-spacing: 0.10em;
  color: rgba(201, 251, 255, 0.95);
  text-transform: uppercase;
}
.bubbleBody {
  margin-top: 8px;
  white-space: pre-wrap;
  font-size: 12px;
  line-height: 1.35;
  opacity: 0.92;
}
.toneNeutral { border-color: rgba(91, 230, 255, 0.22); }
.toneGreen { border-color: rgba(90, 255, 170, 0.30); box-shadow: 0 18px 50px rgba(90, 255, 170, 0.08); }
.toneYellow { border-color: rgba(255, 210, 90, 0.32); box-shadow: 0 18px 50px rgba(255, 210, 90, 0.08); }
.toneRed { border-color: rgba(255, 90, 110, 0.32); box-shadow: 0 18px 50px rgba(255, 90, 110, 0.08); }

#c {
  position: fixed;
  inset: 0;
  width: 100vw;
  height: 100vh;
  display: block;
  z-index: 0;
}

.hud {
  position: fixed;
  left: 20px;
  top: 18px;
  right: 20px;
  display: flex;
  justify-content: space-between;
  z-index: 5;
  pointer-events: none;
}

.hudRight {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  pointer-events: auto;
}

.hudAgentBtn {
  pointer-events: auto;
  height: 34px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(110, 230, 255, 0.28);
  background: rgba(4, 10, 23, 0.45);
  color: rgba(235, 250, 255, 0.92);
  font-weight: 950;
  letter-spacing: 0.12em;
  font-size: 11px;
  cursor: pointer;
  box-shadow:
    0 0 0 1px rgba(80, 200, 255, 0.12),
    0 0 22px rgba(60, 170, 255, 0.18);
  backdrop-filter: blur(12px);
}

.hudAgentBtn.isOpen {
  border-color: rgba(110, 230, 255, 0.45);
  box-shadow:
    0 0 0 1px rgba(80, 200, 255, 0.18),
    0 0 36px rgba(60, 170, 255, 0.28);
}

.agentBackBtn {
  position: fixed;
  left: 18px;
  top: 18px;
  z-index: 9;
  height: 36px;
  padding: 0 14px;
  border-radius: 12px;
  border: 1px solid rgba(110, 230, 255, 0.28);
  background: rgba(4, 10, 23, 0.45);
  color: rgba(235, 250, 255, 0.92);
  font-weight: 950;
  letter-spacing: 0.12em;
  font-size: 11px;
  cursor: pointer;
  box-shadow:
    0 0 0 1px rgba(80, 200, 255, 0.12),
    0 0 22px rgba(60, 170, 255, 0.18);
  backdrop-filter: blur(12px);
}

.title {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: 0.16em;
  color: #c9fbff;
  text-shadow: 0 0 18px rgba(80, 235, 255, 0.45);
}

.subtitle {
  margin-top: 6px;
  font-size: 13px;
  opacity: 0.75;
}

.tagline {
  margin-top: 8px;
  font-size: 12px;
  opacity: 0.66;
}

.hint {
  font-size: 13px;
  opacity: 0.66;
  margin-top: 8px;
}

.overview {
  position: fixed;
  top: 120px;
  left: 20px;
  width: 235px;
  z-index: 5;
  padding: 15px;
  border-radius: 18px;
  background: rgba(8, 17, 34, 0.62);
  border: 1px solid rgba(91, 230, 255, 0.22);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(14px);
}

.boxTitle {
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.13em;
  color: rgba(91, 230, 255, 0.9);
  margin-bottom: 12px;
}

.metric {
  padding: 10px;
  margin-top: 8px;
  border-radius: 12px;
  background: rgba(4, 10, 23, 0.66);
  border: 1px solid rgba(91, 230, 255, 0.13);
}

.metric span {
  display: block;
  font-size: 10px;
  text-transform: uppercase;
  opacity: 0.55;
  letter-spacing: 0.08em;
}

.metric b {
  display: block;
  margin-top: 4px;
  font-size: 16px;
  color: #eaffff;
}

.panel {
  position: fixed;
  right: 20px;
  bottom: 20px;
  width: min(470px, calc(100vw - 40px));
  z-index: 5;
  border-radius: 18px;
  padding: 14px;
  background: rgba(8, 17, 34, 0.62);
  border: 1px solid rgba(91, 230, 255, 0.22);
  box-shadow: 0 18px 50px rgba(0, 0, 0, 0.45);
  backdrop-filter: blur(14px);
}
.hidden { display: none; }

.panelHeader { display:flex; justify-content:space-between; align-items:flex-start; }
.panelTitle { font-weight: 900; font-size: 16px; }
.panelSub { margin-top: 4px; opacity: 0.7; font-size: 12px; }
.badge {
  font-size: 11px;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 950;
  letter-spacing: 0.08em;
  border: 1px solid rgba(91, 230, 255, 0.22);
  background: rgba(4, 10, 23, 0.66);
}
.alertGreen { color: rgba(90, 255, 170, 0.96); border-color: rgba(90, 255, 170, 0.28); box-shadow: 0 0 24px rgba(90, 255, 170, 0.12); }
.alertYellow { color: rgba(255, 210, 90, 0.96); border-color: rgba(255, 210, 90, 0.30); box-shadow: 0 0 24px rgba(255, 210, 90, 0.12); }
.alertRed { color: rgba(255, 90, 110, 0.96); border-color: rgba(255, 90, 110, 0.30); box-shadow: 0 0 24px rgba(255, 90, 110, 0.12); }

.panelBody { margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.kv { border-radius: 12px; padding: 10px; background: rgba(4, 10, 23, 0.66); border: 1px solid rgba(91, 230, 255, 0.13); }
.kv.wide { grid-column: 1 / -1; }
.kv .k { font-size: 10px; opacity: 0.6; text-transform: uppercase; letter-spacing: 0.08em; }
.kv .v { margin-top: 6px; font-weight: 800; }
.statusRow { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.envRow { position: relative; overflow: hidden; cursor: pointer; }
.envRow:hover { border-color: rgba(120,240,255,0.32); }
.envLeft { min-width: 0; }
.envGauge {
  width: 62px;
  height: 62px;
  border-radius: 999px;
  background:
    conic-gradient(var(--c) calc(var(--p) * 1%), rgba(255,255,255,0.08) 0);
  display: grid;
  place-items: center;
  box-shadow: 0 0 28px rgba(120,240,255,0.10);
  flex: 0 0 auto;
}
.envGaugeInner {
  width: 46px;
  height: 46px;
  border-radius: 999px;
  background: rgba(6, 14, 30, 0.78);
  border: 1px solid rgba(91,230,255,0.18);
  display: grid;
  place-items: center;
}
.envGaugeNum { font-size: 14px; font-weight: 950; }
.envGaugeDen { margin-top: -4px; font-size: 10px; opacity: 0.65; font-weight: 900; }
.envRow .k { font-size: 10px; opacity: 0.65; text-transform: uppercase; letter-spacing: 0.12em; }
.envValue {
  margin-top: 8px;
  font-size: 26px;
  font-weight: 950;
  letter-spacing: 0.10em;
  text-transform: uppercase;
}
.envSub { margin-top: 6px; font-size: 11px; opacity: 0.62; }
.envGood .envValue { color: rgba(90,255,170,0.98); text-shadow: 0 0 22px rgba(90,255,170,0.22); }
.envModerate .envValue { color: rgba(255,210,90,0.98); text-shadow: 0 0 22px rgba(255,210,90,0.20); }
.envPoor .envValue { color: rgba(255,90,110,0.98); text-shadow: 0 0 26px rgba(255,90,110,0.25); }
.envPoor { animation: envPulse 1.8s ease-in-out infinite; }
@keyframes envPulse {
  0%, 100% { box-shadow: 0 0 0 rgba(255,90,110,0.0); }
  50% { box-shadow: 0 0 28px rgba(255,90,110,0.12); }
}
.envIndex { font-weight: 950; }

.panelHint { margin-top: 10px; font-size: 12px; opacity: 0.6; font-style: italic; }
.buttons { margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap; }
button {
  pointer-events: auto;
  appearance: none;
  border: 1px solid rgba(91, 230, 255, 0.22);
  background: rgba(4, 10, 23, 0.66);
  color: rgba(235, 250, 255, 0.94);
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 12px;
  font-weight: 900;
  cursor: pointer;
}
button:disabled { opacity: 0.5; cursor: not-allowed; }
.greenBtn { border-color: rgba(90, 255, 170, 0.22); }

.errorBox { position: fixed; left: 18px; right: 18px; bottom: 18px; z-index: 50; padding: 14px; border-radius: 14px; background: rgba(50, 10, 14, 0.78); border: 1px solid rgba(255, 100, 120, 0.5); white-space: pre-wrap; font-size: 12px; }
"""

