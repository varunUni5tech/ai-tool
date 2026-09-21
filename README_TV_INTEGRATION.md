# AI Physics & Mathematics 3D Simulation Engine — TV Application Integration Guide

Welcome to the **API Integration Guide** for the AI 3D Simulation Platform. This document outlines the complete system flow, architecture diagrams, available REST API endpoints, request/response schemas, and step-by-step instructions to integrate this backend and WebGL renderer into a **Smart TV Application** (Android TV, Tizen OS, webOS, or Web-based TV shells).

---

## 1. System Architecture & High-Level Flow

The architecture operates in a **Hybrid Orchestration Model**:

```
 ┌─────────────────────────────────────────────────────────────────────────────────┐
 │                            Smart TV Application Client                          │
 │                                                                                 │
 │   ┌──────────────────────┐    ┌──────────────────────┐    ┌─────────────────┐   │
 │   │  NL Voice/Text Input │    │ Monaco / Spec Store  │    │ Three.js / R3F  │   │
 │   │  (TV Remote / Mic)   │    │  (State & History)   │    │ 3D Viewport     │   │
 │   └──────────┬───────────┘    └──────────▲───────────┘    └────────▲────────┘   │
 └──────────────┼───────────────────────────┼─────────────────────────┼────────────┘
                │                           │                         │
      1. Voice Prompt               2. Validated JSON        3. Coordinates & Rays
      "Show prism dispersion..."         Spec                  for 60fps 3D Scene
                │                           │                         │
 ┌──────────────▼───────────────────────────┴─────────────────────────┴────────────┐
 │                            FastAPI Python Backend                               │
 │                                                                                 │
 │  ┌─────────────────────────┐   ┌───────────────────────┐  ┌──────────────────┐  │
 │  │  AI Prompt Orchestrator │   │  Deterministic Engines│  │ Plotly 3D        │  │
 │  │  (NLP -> JSON Spec)     │──►│  (SymPy / SciPy ODE)  │─►│ HTML Exporter    │  │
 │  └─────────────────────────┘   └───────────────────────┘  └──────────────────┘  │
 └─────────────────────────────────────────────────────────────────────────────────┘
```

### End-to-End Execution Flow
1. **User Voice / Remote Control Action**: The user speaks or types a prompt on the TV (e.g., *"Show rainbow prism dispersion with 60 degree apex angle"*).
2. **AI Spec Generation (`POST /api/v1/simulations/generate`)**: The TV app sends the string to the FastAPI backend. The AI NLP orchestrator parses the physics intent and returns a strict **JSON Simulation Spec**.
3. **Physics Engine Execution (`POST /api/v1/simulations/run`)**: The TV app executes the JSON Spec on the backend Python engine (or local client fallback). SymPy computes exact refractions/trajectories and returns 3D ray points, deviation angles, and kinetic parameters.
4. **3D Scene Rendering**: The TV app feeds the coordinates into Three.js/R3F (or renders the backend HTML endpoint `POST /api/v1/simulations/run/html3d` inside a TV WebView).

---

## 2. API Endpoints Reference

Base URL: `http://<your-backend-host>:8000/api/v1`

---

### Endpoint 1: Health Check & System Status
Use this on TV app startup to check if the Python FastAPI server is active.

- **URL**: `GET /api/v1/health`
- **Headers**: `Accept: application/json`
- **Response `200 OK`**:
```json
{
  "status": "healthy",
  "engine_version": "0.1.0",
  "registered_simulations": [
    { "domain": "mathematics", "simulation_type": "function_plot", "class": "FunctionPlotSimulation" },
    { "domain": "mechanics", "simulation_type": "projectile_motion", "class": "ProjectileSimulation" },
    { "domain": "optics", "simulation_type": "optical_prism", "class": "PrismRefractionSimulation" },
    { "domain": "optics", "simulation_type": "prism_dispersion", "class": "PrismDispersionSimulation" }
  ]
}
```

---

### Endpoint 2: Natural Language Prompt -> JSON Spec Generator
Converts voice commands or typed text from the TV remote into a structured simulation JSON spec.

- **URL**: `POST /api/v1/simulations/generate`
- **Headers**: `Content-Type: application/json`
- **Request Body**:
```json
{
  "prompt": "Show ray of light hitting a 60 degree prism with Cauchy B 1.5",
  "provider": "mock"
}
```

- **Response `200 OK`**:
```json
{
  "simulation_schema_version": "1.0",
  "simulation_type": "prism_dispersion",
  "domain": "optics",
  "objects": [],
  "parameters": {
    "apex_angle": 60.0,
    "incident_angle": 30.0,
    "cauchy_b": 1.5,
    "cauchy_c": 0.004,
    "wavelengths_nm": [700.0, 620.0, 580.0, 530.0, 470.0, 420.0]
  },
  "visualization": {
    "type": "dispersion_spectrum",
    "animated": false,
    "title": "Prism Spectral Dispersion",
    "show_grid": true,
    "color_palette": "viridis"
  },
  "educational": {
    "subject": "Physics",
    "chapter": "Ray Optics",
    "topic": "Dispersion of Light",
    "difficulty": "Class 12"
  }
}
```

---

### Endpoint 3: Run Simulation Physics Engine
Executes deterministic physics calculations from a JSON Spec and returns all 3D geometry coordinates, mathematical results, and optics spectral arrays.

- **URL**: `POST /api/v1/simulations/run`
- **Headers**: `Content-Type: application/json`
- **Request Body**: *(Pass the JSON Spec from Endpoint 2)*

- **Response `200 OK` (Optics Prism Example)**:
```json
{
  "simulation_type": "prism_dispersion",
  "domain": "optics",
  "metadata": {
    "params": {
      "apex_angle": 60.0,
      "incident_angle": 30.0,
      "cauchy_b": 1.5,
      "cauchy_c": 0.004,
      "wavelengths_nm": [700.0, 620.0, 580.0, 530.0, 470.0, 420.0]
    },
    "id": "90195ed8-01c1-4914-97d9-0194aee0b66a"
  },
  "summary": {
    "apex_angle_deg": 60.0,
    "incident_angle_deg": 30.0,
    "cauchy_b": 1.5,
    "cauchy_c": 0.004,
    "wavelengths_count": 6,
    "min_deviation_deg": 49.1858,
    "max_deviation_deg": 54.5955,
    "angular_dispersion_deg": 5.4097
  },
  "data": {
    "spectral_rays": [
      {
        "wavelength_nm": 700.0,
        "refractive_index": 1.50816,
        "color": "#FF0000",
        "deviation_deg": 49.1858,
        "geometry": {
          "prism_vertices": [[-2.0, -1.732], [0.0, 1.732], [2.0, -1.732]],
          "ray_points": [[0.5, -2.598], [-1.0, 0.0], [1.0, 0.0], [-0.96, 2.27]]
        }
      }
    ]
  }
}
```

---

### Endpoint 4: Direct Interactive 3D HTML Exporter (TV WebView Friendly)
Generates an embedded interactive 3D WebGL HTML page. Useful if your Smart TV app prefers rendering 3D scenes inside a native TV `WebView` without custom WebGL wrapper code.

- **URL**: `POST /api/v1/simulations/run/html3d`
- **Headers**: `Content-Type: application/json`
- **Response `200 OK`**: Returns full HTML markup (`text/html`) containing an interactive Plotly 3D WebGL canvas.

---

## 3. Integration Guide for Smart TV App Developers

### Step A: API Service Layer (`apiService.ts`)
Create a centralized API client module in your TV project:

```typescript
const BASE_URL = 'http://YOUR_SERVER_IP:8000/api/v1';

export class TvApiService {
  // 1. Check API Connection Status
  static async checkHealth(): Promise<boolean> {
    try {
      const res = await fetch(`${BASE_URL}/health`, { signal: AbortSignal.timeout(3000) });
      return res.ok;
    } catch {
      return false;
    }
  }

  // 2. Convert Voice Input to Simulation Spec
  static async promptToSpec(voicePrompt: string): Promise<any> {
    const res = await fetch(`${BASE_URL}/simulations/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ prompt: voicePrompt, provider: 'mock' }),
    });
    if (!res.ok) throw new Error('Failed to generate simulation spec');
    return await res.json();
  }

  // 3. Compute Physics Output
  static async runSimulation(spec: any): Promise<any> {
    const res = await fetch(`${BASE_URL}/simulations/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(spec),
    });
    if (!res.ok) throw new Error('Physics execution failed');
    return await res.json();
  }
}
```

---

### Step B: TV Remote Key Controller
Map Smart TV D-Pad remote control buttons to simulation actions:

| TV Remote Button | Functionality | Action Code |
| :--- | :--- | :--- |
| **Select / OK** | Execute Prompt or Trigger Animation | `handleRender()` |
| **Play / Pause** | Play/Pause 3D Ray Animation | `setIsPlaying(!isPlaying)` |
| **D-Pad Left / Right** | Adjust Animation Speed | `setSpeed(s => s +/- 0.2)` |
| **D-Pad Up / Down** | Switch Camera Preset View | `setCameraView('default'/'top')` |
| **Red Color Button** | Reset 3D Viewport Camera | `setCameraView('default')` |

---

### Step C: Supported Physics Datasets & Testcases

1. **Optics Rainbow Dispersion**:
   ```json
   {
     "simulation_type": "prism_dispersion",
     "domain": "optics",
     "parameters": { "apex_angle": 60.0, "incident_angle": 30.0, "cauchy_b": 1.5, "cauchy_c": 0.004, "wavelengths_nm": [700, 620, 580, 530, 470, 420] }
   }
   ```

2. **Kinematics Projectile Motion**:
   ```json
   {
     "simulation_type": "projectile_motion",
     "domain": "mechanics",
     "parameters": { "initial_velocity": 25.0, "launch_angle": 45.0, "initial_height": 0.0, "gravity": 9.81, "time_step": 0.05 }
   }
   ```

3. **Math Calculus & Trigonometry Plotting** (`sin(x)/cos(x)`):
   ```json
   {
     "simulation_type": "function_plot",
     "domain": "mathematics",
     "parameters": { "expression": "sin(x)/cos(x)", "domain": { "min": 0.0, "max": 6.28, "samples": 200 } }
   }
   ```

---

## 4. Running the Backend Server

To expose the backend API to your Smart TV over your local Wi-Fi / LAN network:

```bash
# Navigate to backend directory
cd /path/to/python-ai-simulator

# Activate Python environment & run uvicorn bound to 0.0.0.0
.venv/bin/uvicorn ai_simulation_engine.api.app:app --host 0.0.0.0 --port 8000 --reload
```

Once running, your TV app can query `http://<YOUR_MAC_OR_SERVER_IP>:8000/api/v1/health`.
