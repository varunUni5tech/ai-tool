"""FastAPI main application module."""

import uuid
from typing import Dict, Any
from fastapi import FastAPI, APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

# Ensure registered simulations are loaded
import ai_simulation_engine.simulations  # noqa: F401
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult
from ai_simulation_engine.models.mathematics import FunctionPlotSpec
from ai_simulation_engine.models.physics import ProjectileSpec
from ai_simulation_engine.services.ai_service import AIService
from ai_simulation_engine.services.simulation_service import SimulationService
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.visualization.plots_2d.plotly_backend import PlotlyExporter
from ai_simulation_engine.visualization.plots_3d.plotly_3d_backend import Plotly3DExporter
from ai_simulation_engine.errors.exceptions import SimulationEngineError


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Mathematical & Physics Simulation Engine API",
    description="Production-grade AI-orchestrated math/physics simulation engine",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database cache for demo / GET /simulations/{id}
SIMULATION_STORE: Dict[str, SimulationResult] = {}


class PromptRequest(BaseModel):
    prompt: str = Field(description="Natural language simulation description")
    provider: str = Field(default="mock", description="AI provider: mock | openai")


router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint and list of registered simulations."""
    return {
        "status": "healthy",
        "engine_version": "0.1.0",
        "registered_simulations": SimulationRegistry.list_registered(),
    }


@router.post("/simulations/generate", response_model=SimulationSpec, status_code=status.HTTP_200_OK)
def generate_simulation_spec(req: PromptRequest):
    """Generate a validated SimulationSpec from a natural language prompt."""
    try:
        spec = AIService.generate_spec_from_prompt(req.prompt, provider_name=req.provider)
        return spec
    except SimulationEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/run", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def run_simulation(spec: SimulationSpec):
    """Execute a simulation from a validated spec and return computed state & results."""
    try:
        result = SimulationService.execute_simulation(spec)
        sim_id = str(uuid.uuid4())
        SIMULATION_STORE[sim_id] = result
        result.metadata["id"] = sim_id
        return result
    except SimulationEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/run/html", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def run_simulation_html(spec: SimulationSpec):
    """Execute simulation from spec and return an interactive Plotly HTML chart."""
    try:
        result = SimulationService.execute_simulation(spec)
        html_content = PlotlyExporter.render_to_html(result)
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/run/html3d", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def run_simulation_html3d(spec: SimulationSpec):
    """Execute simulation from spec and return an interactive 3D Plotly HTML chart."""
    try:
        result = SimulationService.execute_simulation(spec)
        html_content = Plotly3DExporter.render_prism_3d_html(result)
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/generate-and-run/html", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def generate_and_run_html(req: PromptRequest):
    """Full pipeline: NL Prompt -> Spec -> Execute -> Interactive Plotly HTML web visualization."""
    try:
        spec = AIService.generate_spec_from_prompt(req.prompt, provider_name=req.provider)
        result = SimulationService.execute_simulation(spec)
        html_content = PlotlyExporter.render_to_html(result)
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/generate-and-run/html3d", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def generate_and_run_html3d(req: PromptRequest):
    """Full pipeline: NL Prompt -> Spec -> Execute -> Interactive 3D Plotly HTML web visualization."""
    try:
        spec = AIService.generate_spec_from_prompt(req.prompt, provider_name=req.provider)
        result = SimulationService.execute_simulation(spec)
        html_content = Plotly3DExporter.render_prism_3d_html(result)
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/math/graph", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def math_graph_express(param: FunctionPlotSpec):
    """Express endpoint to quickly plot a mathematical function y = f(x)."""
    spec = SimulationSpec(
        simulation_type="function_plot",
        domain="mathematics",
        parameters=param.model_dump(),
    )
    return run_simulation(spec)


@router.post("/physics/simulate", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def physics_simulate_express(param: ProjectileSpec):
    """Express endpoint to run a projectile motion kinematics simulation."""
    spec = SimulationSpec(
        simulation_type="projectile_motion",
        domain="mechanics",
        parameters=param.model_dump(),
    )
    return run_simulation(spec)


@router.get("/simulations/{sim_id}", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def get_simulation_by_id(sim_id: str):
    """Fetch previously computed simulation result by ID."""
    if sim_id not in SIMULATION_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation ID '{sim_id}' not found.")
    return SIMULATION_STORE[sim_id]


@router.get("/visualize/{sim_id}", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def visualize_simulation_by_id(sim_id: str):
    """Render interactive HTML web graph for a computed simulation ID."""
    if sim_id not in SIMULATION_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation ID '{sim_id}' not found.")
    result = SIMULATION_STORE[sim_id]
    html_content = PlotlyExporter.render_to_html(result)
    return HTMLResponse(content=html_content)


# Register router under root AND /api/v1 prefix to support both route formats
app.include_router(router)
app.include_router(router, prefix="/api/v1")
