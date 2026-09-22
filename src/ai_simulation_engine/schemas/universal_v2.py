"""Universal Simulation Specification 2.0 (Pydantic v2)."""

from typing import List, Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field


class SimulationMeta(BaseModel):
    type: str = Field(description="Simulation type identifier e.g. orbital_motion, projectile_motion, function_plot")
    domain: str = Field(description="Domain e.g. physics, mathematics, astronomy, mechanics, optics, engineering")
    title: Optional[str] = Field(default=None, description="Human-readable title")
    description: Optional[str] = Field(default=None, description="Short summary of phenomenon")
    dimension: Literal["1d", "2d", "3d"] = Field(default="2d", description="Spatial dimensionality")


class TimeConfig(BaseModel):
    start: float = Field(default=0.0, description="Start time in seconds")
    end: float = Field(default=10.0, description="End time in seconds")
    step: float = Field(default=0.05, description="Time step delta t in seconds")
    unit: str = Field(default="s", description="Time unit")


class EnvironmentConfig(BaseModel):
    units: str = Field(default="SI", description="Unit system e.g. SI")
    time: TimeConfig = Field(default_factory=TimeConfig)
    ambient_temperature: Optional[float] = Field(default=None, description="Ambient temp K")
    gravity: Optional[float] = Field(default=None, description="Gravitational acceleration m/s^2")


class PhysicalObject(BaseModel):
    id: Optional[str] = None
    name: str = Field(default="object", description="Object identifier name e.g. sun, earth, projectile, mass_1")
    type: str = Field(default="particle", description="Object primitive type e.g. particle, body, prism, wave")
    mass: Optional[float] = Field(default=None, description="Mass in kg")
    charge: Optional[float] = Field(default=None, description="Electric charge in C")
    position: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0], description="Initial position [x,y,z]")
    velocity: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0], description="Initial velocity [vx,vy,vz]")
    color: Optional[str] = Field(default="#00F0FF", description="Visualization color hex")
    radius: Optional[float] = Field(default=None, description="Physical visual radius")
    properties: Dict[str, Any] = Field(default_factory=dict)


class PhysicalModel(BaseModel):
    type: str = Field(default="standard", description="Governing physical/mathematical model name")
    equations: List[str] = Field(default_factory=list, description="Latex or text governing equations")
    assumptions: List[str] = Field(default_factory=list, description="Explicit physics assumptions")


class SolverConfig(BaseModel):
    type: str = Field(default="numerical_ode", description="Solver category e.g. numerical_ode, analytical, symbolic, particle_integrator")
    method: str = Field(default="RK45", description="Numerical integration algorithm")
    parameters: Dict[str, Any] = Field(default_factory=dict)


class EducationMeta(BaseModel):
    level: Literal["elementary", "middle_school", "high_school", "undergraduate", "engineering"] = Field(
        default="high_school", description="Target educational depth"
    )
    subject: str = Field(default="Physics", description="Subject area")
    chapter: Optional[str] = None
    topic: Optional[str] = None
    show_equations: bool = True
    show_values: bool = True
    show_explanation: bool = True


class CameraConfig(BaseModel):
    position: List[float] = Field(default_factory=lambda: [0.0, 0.0, 10.0])
    target: List[float] = Field(default_factory=lambda: [0.0, 0.0, 0.0])


class AxesConfig(BaseModel):
    x_label: str = "X"
    y_label: str = "Y"
    z_label: str = "Z"
    grid: bool = True


class VisualizationSpec(BaseModel):
    type: str = Field(default="2d_plot", description="Visualization render type")
    camera: CameraConfig = Field(default_factory=CameraConfig)
    axes: AxesConfig = Field(default_factory=AxesConfig)
    objects: List[Dict[str, Any]] = Field(default_factory=list)
    vectors: List[Dict[str, Any]] = Field(default_factory=list)
    trails: List[Dict[str, Any]] = Field(default_factory=list)
    animation: Dict[str, Any] = Field(default_factory=dict)


class UniversalSimulationSpec(BaseModel):
    """Universal Machine-Readable Simulation Specification v2.0."""

    schema_version: str = Field(default="2.0", description="Schema specification version")
    simulation: SimulationMeta
    environment: EnvironmentConfig = Field(default_factory=EnvironmentConfig)
    objects: List[PhysicalObject] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    constants: Dict[str, Any] = Field(default_factory=dict)
    initial_conditions: Dict[str, Any] = Field(default_factory=dict)
    model: PhysicalModel = Field(default_factory=PhysicalModel)
    solver: SolverConfig = Field(default_factory=SolverConfig)
    outputs: List[str] = Field(default_factory=list)
    visualization: VisualizationSpec = Field(default_factory=VisualizationSpec)
    education: EducationMeta = Field(default_factory=EducationMeta)

    @classmethod
    def from_v1_dict(cls, data: Dict[str, Any]) -> "UniversalSimulationSpec":
        """Convert a legacy v1.0 spec dictionary into a Universal v2.0 spec."""
        sim_type = data.get("simulation_type", "function_plot")
        domain = data.get("domain", "physics")
        params = data.get("parameters", {})
        viz = data.get("visualization", {})
        edu = data.get("educational", {}) or data.get("education", {})

        return cls(
            schema_version="2.0",
            simulation=SimulationMeta(
                type=sim_type,
                domain=domain,
                dimension="3d" if "3d" in str(viz.get("type", "")).lower() else "2d",
            ),
            parameters=params,
            visualization=VisualizationSpec(
                type=viz.get("type", "2d_plot"),
                axes=AxesConfig(
                    x_label=viz.get("x_label", "X"),
                    y_label=viz.get("y_label", "Y"),
                ),
            ),
            education=EducationMeta(
                subject=edu.get("subject", "Physics"),
                chapter=edu.get("chapter"),
                topic=edu.get("topic"),
                level="high_school",
            ),
        )
