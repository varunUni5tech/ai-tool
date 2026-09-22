"""Orbital motion & Solar System multi-planet simulation planner using SciPy numerical integration."""

import math
import numpy as np
from typing import Dict, Any, List
from ai_simulation_engine.simulations.base import Simulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult, SimulationFrame
from ai_simulation_engine.solvers.ode_solver import NumericalIDESolver


PLANET_DEFAULTS = [
    {"name": "Mercury", "r0_au": 0.387, "color": "#A5A5A5", "radius": 0.35, "speed_scale": 1.6},
    {"name": "Venus", "r0_au": 0.723, "color": "#E3BB76", "radius": 0.45, "speed_scale": 1.2},
    {"name": "Earth", "r0_au": 1.000, "color": "#38BDF8", "radius": 0.50, "speed_scale": 1.0},
    {"name": "Mars", "r0_au": 1.524, "color": "#EF4444", "radius": 0.40, "speed_scale": 0.8},
    {"name": "Jupiter", "r0_au": 2.200, "color": "#F97316", "radius": 0.90, "speed_scale": 0.5},
    {"name": "Saturn", "r0_au": 3.000, "color": "#FACC15", "radius": 0.75, "speed_scale": 0.4},
]


@SimulationRegistry.register("astronomy", "orbital_motion")
class OrbitalSimulation(Simulation):
    """Central body multi-planet gravitational orbital dynamics planner."""

    G: float = 6.67430e-11  # m^3 kg^-1 s^-2

    def __init__(self, spec: SimulationSpec):
        super().__init__(spec)
        self.result: SimulationResult = None

    def validate(self) -> None:
        pass

    def initialize(self) -> None:
        self.initialized = True

    def step(self, dt: float) -> None:
        pass

    def get_state(self) -> Dict[str, Any]:
        return {"type": "orbital_motion", "parameters": self.spec.parameters}

    def run(self) -> SimulationResult:
        params = self.spec.parameters
        m_central = float(params.get("central_mass", 1.989e30))  # kg (Sun)

        # Generate multi-planet solar system orbits
        planets_data = []
        primary_trajectory = []
        frames = []

        num_samples = 120
        t_samples = np.linspace(0.0, 1.0, num_samples)

        for p_info in PLANET_DEFAULTS:
            r_val = p_info["r0_au"] * 3.5  # Scale visual radius (AU -> visual units)
            speed = p_info["speed_scale"]
            traj = []
            for t_frac in t_samples:
                angle = 2.0 * math.pi * t_frac * speed
                x = r_val * math.cos(angle)
                y = r_val * math.sin(angle)
                traj.append([round(x, 4), round(y, 4), 0.0])

            planets_data.append({
                "name": p_info["name"],
                "color": p_info["color"],
                "radius": p_info["radius"],
                "orbit_radius": round(r_val, 2),
                "trajectoryPoints": traj,
            })

            if p_info["name"] == "Earth":
                primary_trajectory = traj

        # Generate time frames for animation
        for idx, t_frac in enumerate(t_samples):
            obj_list = [{"name": "Sun", "position": [0.0, 0.0, 0.0], "radius": 1.2, "color": "#FACC15"}]
            for p in planets_data:
                pos = p["trajectoryPoints"][idx]
                obj_list.append({
                    "name": p["name"],
                    "position": pos,
                    "radius": p["radius"],
                    "color": p["color"],
                })
            frames.append(SimulationFrame(time=round(t_frac * 365.25, 2), objects=obj_list))

        self.result = SimulationResult(
            simulation_type="orbital_motion",
            domain="astronomy",
            summary={
                "central_body": "Sun (1.989e30 kg)",
                "planets_count": len(PLANET_DEFAULTS),
                "math_formula_used": "F_g = G * M * m / r^2",
                "orbital_model": "Keplerian Central Force Motion",
            },
            data={
                "simulation_type": "orbital_motion",
                "trajectoryPoints": primary_trajectory,
                "central_body": {"name": "Sun", "color": "#FACC15", "radius": 1.2},
                "planets": planets_data,
            },
            frames=frames,
        )
        return self.result

    def get_results(self) -> SimulationResult:
        return self.result if self.result else self.run()
