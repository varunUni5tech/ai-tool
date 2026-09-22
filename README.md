# Universal AI-Driven Physics & Mathematics Simulation Platform

Production-grade, modular AI-orchestrated math and physics simulation platform supporting educational and engineering-level simulations.

Natural language request → Ollama / AI Provider → Universal Specification 2.0 → Pydantic Validation & Repair Loop → Simulation Planner & Capability Registry → Deterministic Math/Physics Engine (NumPy/SciPy/SymPy) → Numerical Solver → Visualization Router (2D/3D Plotly, Three.js, Flutter).

---

## Universal System Architecture

```
User Prompt (Natural Language)
        │
        ▼
   LLMProvider (Ollama / OpenAI / Mock)
        │
        ▼
 Universal Spec 2.0 (JSON)
        │
        ▼
 Pydantic v2 Validation ─── Invalid ──► LLM Repair Loop (max 3 attempts)
        │
        ▼ (Valid)
 Capability & Simulation Registry
        │
        ▼
 Simulation Planner & Reusable Primitives (Body, Particle, Force, Gravity, Vector3D)
        │
        ▼
 Deterministic Math/Physics Solvers (NumPy, SciPy solve_ivp, SymPy)
        │
        ▼
 Simulation Data & Trajectories
        │
        ▼
 Visualization Router (2D Plotly, 3D Orbital/Prism Three.js, Flutter JSON)
        │
        ▼
 API Response (JSON & Interactive HTML)
```

---

## Security Model
- **Zero Arbitrary LLM Execution**: The LLM NEVER generates or executes arbitrary Python code, JavaScript, or shell scripts.
- **Strict Specification Schema**: The LLM produces machine-readable JSON matching `UniversalSimulationSpec` (v2.0).
- **Deterministic Math Engine**: All actual physical calculations, orbital numerical integration, matrix math, and ray-tracing are computed deterministically by verified Python solvers.

---

## Environment Configuration

Configure options via environment variables or `.env` file:

```env
# AI & LLM Provider Configuration
LLM_PROVIDER=ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=qwen3

# Server Settings
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Validation & Repair Loop Settings
SIMULATION_MAX_REPAIR_ATTEMPTS=3

# Numerical Solver Defaults
ODE_SOLVER_METHOD=RK45
SOLVER_RTOL=1e-6
SOLVER_ATOL=1e-8
```

---

## Ollama Local Setup

1. **Install Ollama**:
   ```bash
   brew install ollama
   ```
2. **Start Local Ollama Service**:
   ```bash
   ollama serve
   ```
3. **Pull Your Preferred Model**:
   ```bash
   ollama pull qwen3
   # or: ollama pull llama3.1
   ```

---

## Quick Start & Running

### 1. Setup Virtual Environment & Dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Run Test Suite
```bash
pytest -v
```

### 3. Start FastAPI Server
```bash
uvicorn ai_simulation_engine.api.app:app --reload --port 8000
```
Visit http://localhost:8000/docs for Swagger API documentation.

---

## API Usage Examples

### 1. Universal Simulation Pipeline (`POST /simulate`)
```bash
curl -X POST "http://localhost:8000/simulate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Show Earth orbiting the Sun",
       "provider": "ollama"
     }'
```

### 2. Standard AI Specification Generator (`POST /simulations/generate`)
```bash
curl -X POST "http://localhost:8000/simulations/generate" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Show projectile motion with initial velocity 25 m/s at 30 degrees",
       "provider": "ollama"
     }'
```

### 3. Interactive Web Visualization Exporter (`POST /simulations/generate-and-run/html3d`)
```bash
curl -X POST "http://localhost:8000/simulations/generate-and-run/html3d" \
     -H "Content-Type: application/json" \
     -d '{
       "prompt": "Show light dispersion through a prism",
       "provider": "ollama"
     }'
```

---

## Supported Core Capabilities

1. **Orbital Motion** (`astronomy` / `orbital_motion`): Central force two-body gravitational dynamics integrated with SciPy `solve_ivp` RK45 solver.
2. **Simple Harmonic Motion** (`mechanics` / `simple_harmonic_motion`): Mass-spring Hooke's Law oscillations $(x(t), v(t))$.
3. **2nd Order Control System** (`engineering` / `second_order_control_system`): Step response transfer functions ($G(s) = \frac{\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}$).
4. **Projectile Motion** (`mechanics` / `projectile_motion`): 2D trajectory kinematics under constant gravity.
5. **Math Function Plotting** (`mathematics` / `function_plot`): Safe mathematical expression evaluation over custom domains.
6. **Prism Dispersion & Refraction** (`optics` / `prism_dispersion`): Multi-wavelength Cauchy spectral dispersion and Snell's law ray tracing.

---

## How to Extend the Platform

### 1. Add a New Simulation Capability
Add capability metadata in `src/ai_simulation_engine/simulations/capabilities.py`:
```python
CapabilityRegistry.register(
    SimulationCapability(
        name="double_pendulum",
        domain="mechanics",
        description="Chaotic double pendulum motion under gravity.",
        required_parameters=["length1", "length2", "mass1", "mass2"],
    )
)
```

### 2. Implement the Simulation Planner
Implement class subclassing `Simulation` and register with `@SimulationRegistry.register(domain, name)`:
```python
@SimulationRegistry.register("mechanics", "double_pendulum")
class DoublePendulumSimulation(Simulation):
    def run(self) -> SimulationResult:
        # Compute trajectory using SciPy solve_ivp
        ...
```

### 3. Add a New LLM Provider
Implement `AIProvider` in `src/ai_simulation_engine/ai/providers/` and register in `AIProviderFactory`.
