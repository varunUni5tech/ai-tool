"""Capability registry defining supported simulations, parameters, domains, and solvers."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class SimulationCapability(BaseModel):
    name: str = Field(description="Unique capability identifier e.g. orbital_motion")
    domain: str = Field(description="Domain e.g. astronomy, physics, mathematics, engineering")
    description: str = Field(description="Summary of simulation capability")
    required_parameters: List[str] = Field(default_factory=list)
    optional_parameters: Dict[str, Any] = Field(default_factory=dict)
    supported_dimensions: List[str] = Field(default_factory=lambda: ["2d", "3d"])
    supported_visualization_types: List[str] = Field(default_factory=lambda: ["2d_plot", "3d_scene", "3d_orbit"])
    default_solver: str = "numerical_ode"
    supported_education_levels: List[str] = Field(
        default_factory=lambda: ["elementary", "middle_school", "high_school", "undergraduate", "engineering"]
    )


class CapabilityRegistry:
    """Registry managing available capabilities exposed to the LLM system prompt."""

    _capabilities: Dict[str, SimulationCapability] = {}

    @classmethod
    def register(cls, capability: SimulationCapability):
        cls._capabilities[capability.name] = capability

    @classmethod
    def get(cls, name: str) -> Optional[SimulationCapability]:
        return cls._capabilities.get(name)

    @classmethod
    def list_all(cls) -> List[SimulationCapability]:
        return list(cls._capabilities.values())

    @classmethod
    def generate_prompt_summary(cls) -> str:
        """Format available capabilities for system prompt injection."""
        lines = ["SUPPORTED SIMULATION CAPABILITIES AND SCHEMAS:"]
        for cap in cls._capabilities.values():
            lines.append(f"- type: '{cap.name}' | domain: '{cap.domain}'")
            lines.append(f"  description: {cap.description}")
            lines.append(f"  req_params: {cap.required_parameters}")
            lines.append(f"  opt_params: {cap.optional_parameters}")
            lines.append(f"  viz_types: {cap.supported_visualization_types}")
            lines.append("")
        return "\n".join(lines)


# Register initial core capabilities
CapabilityRegistry.register(
    SimulationCapability(
        name="projectile_motion",
        domain="mechanics",
        description="2D projectile trajectory under constant gravitational acceleration.",
        required_parameters=["initial_velocity", "launch_angle"],
        optional_parameters={"initial_height": 0.0, "gravity": 9.81},
        supported_dimensions=["2d"],
        supported_visualization_types=["2d_plot", "2d_trajectory", "trajectory_2d"],
        default_solver="numerical_ode",
    )
)

CapabilityRegistry.register(
    SimulationCapability(
        name="prism_dispersion",
        domain="optics",
        description="Refraction and chromatic dispersion of light wavelengths through a prism.",
        required_parameters=["apex_angle", "incident_angle"],
        optional_parameters={"cauchy_b": 1.5, "cauchy_c": 0.004},
        supported_dimensions=["2d", "3d"],
        supported_visualization_types=["dispersion_spectrum", "ray_diagram", "3d_scene"],
        default_solver="analytical",
    )
)

CapabilityRegistry.register(
    SimulationCapability(
        name="function_plot",
        domain="mathematics",
        description="2D & 3D mathematical function curves (e.g. sin(x), cos(x), exp(-x)*sin(x)).",
        required_parameters=["expression"],
        optional_parameters={"domain_min": -10.0, "domain_max": 10.0, "samples": 200},
        supported_dimensions=["2d", "3d"],
        supported_visualization_types=["2d_plot", "function_plot", "line_chart"],
        default_solver="analytical",
    )
)

CapabilityRegistry.register(
    SimulationCapability(
        name="orbital_motion",
        domain="astronomy",
        description="Gravitational two-body central force orbital dynamics (Earth-Sun, Satellite-Earth, etc.).",
        required_parameters=["central_mass", "orbiting_mass", "semi_major_axis_m"],
        optional_parameters={"eccentricity": 0.0167, "orbital_period_s": 31558149.76},
        supported_dimensions=["2d", "3d"],
        supported_visualization_types=["3d_orbit", "3d_scene", "2d_plot"],
        default_solver="numerical_ode",
    )
)

CapabilityRegistry.register(
    SimulationCapability(
        name="simple_harmonic_motion",
        domain="mechanics",
        description="Oscillation of a mass-spring system or simple pendulum under Hooke's Law.",
        required_parameters=["mass", "spring_constant"],
        optional_parameters={"initial_displacement": 1.0, "damping": 0.0},
        supported_dimensions=["1d", "2d"],
        supported_visualization_types=["2d_plot", "particle_animation", "line_chart"],
        default_solver="numerical_ode",
    )
)

CapabilityRegistry.register(
    SimulationCapability(
        name="second_order_control_system",
        domain="engineering",
        description="Step response of a 2nd order dynamic system defined by natural frequency and damping ratio.",
        required_parameters=["omega_n", "zeta"],
        optional_parameters={"step_amplitude": 1.0},
        supported_dimensions=["2d"],
        supported_visualization_types=["2d_plot", "line_chart"],
        default_solver="numerical_ode",
    )
)
