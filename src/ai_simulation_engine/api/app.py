"""FastAPI main application module with rich request & engine execution logging."""

import time
import uuid
from typing import Dict, Any
from fastapi import FastAPI, APIRouter, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Ensure registered simulations are loaded
import ai_simulation_engine.simulations  # noqa: F401
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult
from ai_simulation_engine.models.mathematics import FunctionPlotSpec
from ai_simulation_engine.models.physics import ProjectileSpec
from ai_simulation_engine.services.ai_service import AIService
from ai_simulation_engine.ai.providers.factory import AIProviderFactory
from ai_simulation_engine.services.simulation_service import SimulationService
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.visualization.plots_2d.plotly_backend import PlotlyExporter
from ai_simulation_engine.visualization.plots_3d.plotly_3d_backend import Plotly3DExporter
from ai_simulation_engine.errors.exceptions import SimulationEngineError
from ai_simulation_engine.config.logging import logger


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


@app.middleware("http")
async def log_requests_middleware(request: Request, call_next):
    """Middleware to log HTTP method, path, request body/payload, processing duration, and response code."""
    start_time = time.time()
    client_ip = request.client.host if request.client else 'local'
    
    # Read and log request body if present (for POST/PUT/PATCH)
    body_str = ""
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode("utf-8")
            # Re-populate request body stream so downstream route handlers can read it
            async def receive():
                return {"type": "http.request", "body": body_bytes}
            request = Request(request.scope, receive=receive)
        except Exception:
            body_str = "<failed to parse body>"
            
    log_payload_msg = f" | Payload: {body_str}" if body_str else ""
    logger.info(f"--> Incoming HTTP Request: {request.method} {request.url.path} from {client_ip}{log_payload_msg}")
    
    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000
        logger.info(f"<-- Completed HTTP Request: {request.method} {request.url.path} | Status: {response.status_code} | Duration: {duration_ms:.2f}ms")
        return response
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        logger.error(f"<-- Failed HTTP Request: {request.method} {request.url.path} | Duration: {duration_ms:.2f}ms | Error: {str(e)}")
        raise e


# In-memory database cache for demo / GET /simulations/{id}
SIMULATION_STORE: Dict[str, SimulationResult] = {}


class PromptRequest(BaseModel):
    prompt: str = Field(description="Natural language simulation description")
    provider: str = Field(default="mock", description="AI provider: mock | openai")


router = APIRouter()


@router.get("/health", status_code=status.HTTP_200_OK)
def health_check():
    """Health check endpoint and list of registered simulations."""
    registered = SimulationRegistry.list_registered()
    logger.info(f"[HEALTH] Health check ok. Active registered simulations: {len(registered)}")
    return {
        "status": "healthy",
        "engine_version": "0.1.0",
        "registered_simulations": registered,
    }


@router.post("/simulations/generate", status_code=status.HTTP_200_OK)
def generate_simulation_spec(req: PromptRequest):
    """Generate a 3D simulation payload directly from AI natural language prompt."""
    logger.info(f"[AI GENERATE] Prompt received: '{req.prompt}' (provider={req.provider})")
    try:
        provider = AIProviderFactory.get_provider(req.provider)
        spec = provider.generate_spec(req.prompt)
        logger.info(f"[AI GENERATE SUCCESS] Generated payload via AI provider '{req.provider}'")
        return spec
    except SimulationEngineError as e:
        logger.error(f"[AI GENERATE ERROR] Failed to generate spec for prompt '{req.prompt}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/run", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def run_simulation(spec: SimulationSpec):
    """Execute a simulation from a validated spec and return computed state & results."""
    logger.info(f"[ENGINE RUN] Executing simulation domain='{spec.domain}', type='{spec.simulation_type}' with params={spec.parameters}")
    try:
        start_t = time.time()
        result = SimulationService.execute_simulation(spec)
        elapsed_ms = (time.time() - start_t) * 1000

        sim_id = str(uuid.uuid4())
        SIMULATION_STORE[sim_id] = result
        result.metadata["id"] = sim_id

        logger.info(f"[ENGINE RUN SUCCESS] Simulation executed in {elapsed_ms:.2f}ms. ID: {sim_id}. Summary: {result.summary}")
        return result
    except SimulationEngineError as e:
        logger.error(f"[ENGINE RUN ERROR] Execution failed for domain='{spec.domain}', type='{spec.simulation_type}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/run/html", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def run_simulation_html(spec: SimulationSpec):
    """Execute simulation from spec and return an interactive Plotly HTML chart."""
    logger.info(f"[ENGINE HTML 2D] Generating 2D HTML chart for domain='{spec.domain}', type='{spec.simulation_type}'")
    try:
        result = SimulationService.execute_simulation(spec)
        html_content = PlotlyExporter.render_to_html(result)
        logger.info(f"[ENGINE HTML 2D SUCCESS] Rendered 2D HTML chart ({len(html_content)} bytes)")
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        logger.error(f"[ENGINE HTML 2D ERROR] Failed to render 2D HTML chart: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/run/html3d", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def run_simulation_html3d(spec: SimulationSpec):
    """Execute simulation from spec and return an interactive 3D Plotly HTML chart."""
    logger.info(f"[ENGINE HTML 3D] Generating 3D Plotly chart for domain='{spec.domain}', type='{spec.simulation_type}'")
    try:
        result = SimulationService.execute_simulation(spec)
        html_content = Plotly3DExporter.render_prism_3d_html(result)
        logger.info(f"[ENGINE HTML 3D SUCCESS] Rendered 3D HTML chart ({len(html_content)} bytes)")
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        logger.error(f"[ENGINE HTML 3D ERROR] Failed to render 3D HTML chart: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/generate-and-run/html", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def generate_and_run_html(req: PromptRequest):
    """Full pipeline: NL Prompt -> Spec -> Execute -> Interactive Plotly HTML web visualization."""
    logger.info(f"[PIPELINE 2D] Generate & Run 2D HTML for prompt: '{req.prompt}'")
    try:
        spec = AIService.generate_spec_from_prompt(req.prompt, provider_name=req.provider)
        result = SimulationService.execute_simulation(spec)
        html_content = PlotlyExporter.render_to_html(result)
        logger.info(f"[PIPELINE 2D SUCCESS] Rendered 2D HTML visualization for prompt '{req.prompt}'")
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        logger.error(f"[PIPELINE 2D ERROR] Pipeline failed for prompt '{req.prompt}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/simulations/generate-and-run/html3d", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def generate_and_run_html3d(req: PromptRequest):
    """Full pipeline: NL Prompt -> Spec -> Execute -> Interactive 3D Plotly HTML web visualization."""
    logger.info(f"[PIPELINE 3D] Generate & Run 3D HTML for prompt: '{req.prompt}'")
    try:
        spec = AIService.generate_spec_from_prompt(req.prompt, provider_name=req.provider)
        result = SimulationService.execute_simulation(spec)
        html_content = Plotly3DExporter.render_prism_3d_html(result)
        logger.info(f"[PIPELINE 3D SUCCESS] Rendered 3D HTML visualization for prompt '{req.prompt}'")
        return HTMLResponse(content=html_content)
    except SimulationEngineError as e:
        logger.error(f"[PIPELINE 3D ERROR] Pipeline failed for prompt '{req.prompt}': {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/math/graph", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def math_graph_express(param: FunctionPlotSpec):
    """Express endpoint to quickly plot a mathematical function y = f(x)."""
    logger.info(f"[EXPRESS MATH] Plotting math expression: '{param.expression}'")
    spec = SimulationSpec(
        simulation_type="function_plot",
        domain="mathematics",
        parameters=param.model_dump(),
    )
    return run_simulation(spec)


@router.post("/physics/simulate", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def physics_simulate_express(param: ProjectileSpec):
    """Express endpoint to run a projectile motion kinematics simulation."""
    logger.info(f"[EXPRESS PHYSICS] Simulating projectile v0={param.initial_velocity} m/s, launch_angle={param.launch_angle}°")
    spec = SimulationSpec(
        simulation_type="projectile_motion",
        domain="mechanics",
        parameters=param.model_dump(),
    )
    return run_simulation(spec)


@router.get("/simulations/{sim_id}", response_model=SimulationResult, status_code=status.HTTP_200_OK)
def get_simulation_by_id(sim_id: str):
    """Fetch previously computed simulation result by ID."""
    logger.info(f"[FETCH RESULT] Looking up simulation ID: '{sim_id}'")
    if sim_id not in SIMULATION_STORE:
        logger.warning(f"[FETCH RESULT NOT FOUND] Simulation ID '{sim_id}' not in cache.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation ID '{sim_id}' not found.")
    return SIMULATION_STORE[sim_id]


@router.get("/visualize/{sim_id}", response_class=HTMLResponse, status_code=status.HTTP_200_OK)
def visualize_simulation_by_id(sim_id: str):
    """Render interactive HTML web graph for a computed simulation ID."""
    logger.info(f"[VISUALIZE ID] Rendering HTML for simulation ID: '{sim_id}'")
    if sim_id not in SIMULATION_STORE:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Simulation ID '{sim_id}' not found.")
    result = SIMULATION_STORE[sim_id]
    html_content = PlotlyExporter.render_to_html(result)
    return HTMLResponse(content=html_content)


# Register router under root AND /api/v1 prefix to support both route formats
app.include_router(router)
app.include_router(router, prefix="/api/v1")
