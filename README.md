# AI Mathematical & Physics Simulation Engine

Production-grade, modular AI-orchestrated math/physics simulation platform.

Natural language request → AI produces a structured JSON simulation spec → spec is validated → deterministic math/physics engine computes results → visualization layer renders output.

## Architecture

```
User request
  → AI Layer (intent → structured JSON spec)
  → Pydantic + JSON-Schema validation
  → Simulation Planner (registry lookup)
  → Math/Physics Engine (SymPy/NumPy/SciPy)
  → Numerical Solver
  → Simulation State/Frames (engine-agnostic data)
  → Visualization Layer (Matplotlib/Plotly)
  → API response (frontend-agnostic JSON)
```

## Quick Start

### 1. Setup Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
```

### 2. Run Tests
```bash
pytest -v
```

### 3. Run FastAPI Application
```bash
uvicorn ai_simulation_engine.api.app:app --reload --port 8000
```
Visit http://localhost:8000/docs for the interactive Swagger documentation.

### 4. CLI Usage
```bash
# List registered simulations
ai-sim list

# Generate simulation spec from NL prompt
ai-sim generate "Plot sin(x) from 0 to 2pi"

# Run projectile simulation directly
ai-sim run --domain mechanics --type projectile_motion --param velocity=20 --param angle=45

# Visualize a simulation output
ai-sim visualize --domain optics --type prism_dispersion --output outputs/dispersion.png
```

## Supported Phase 1 Simulations

1. **Math Function Plotting** (`mathematics` / `function_plot`): Safe expression evaluation over designated domains ($x_{min}, x_{max}$).
2. **Projectile Motion** (`mechanics` / `projectile_motion`): Kinematics & ODE integration of projectile trajectory $(x(t), y(t))$ under gravity.
3. **Prism Refraction** (`optics` / `optical_prism`): Snell's law ray tracing through triangular prisms with Total Internal Reflection (TIR) detection.
4. **Prism Dispersion** (`optics` / `prism_dispersion`): Multi-wavelength spectral ray tracing using Cauchy's dispersion formula ($n(\lambda) = B + C/\lambda^2$).

## How to Extend

- **Add a new Simulation**: Implement `Simulation` in `src/ai_simulation_engine/simulations/` and register via `@SimulationRegistry.register(domain, type_name)`.
- **Add a new AI Provider**: Implement `AIProvider` interface in `src/ai_simulation_engine/ai/providers/`.
- **Add a Visualization Backend**: Implement standard exporter in `src/ai_simulation_engine/visualization/`.
