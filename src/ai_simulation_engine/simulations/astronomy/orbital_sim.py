"""Orbital motion simulation planner using SciPy numerical integration."""

import math
import numpy as np
from typing import Dict, Any, List
from ai_simulation_engine.simulations.base import Simulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult, SimulationFrame
from ai_simulation_engine.solvers.ode_solver import NumericalIDESolver
from ai_simulation_engine.physics_engine.primitives import GravityForce


@SimulationRegistry.register("astronomy", "orbital_motion")
class OrbitalSimulation(Simulation):
    """Central body two-body gravitational orbital dynamics planner."""

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
        # Extract celestial parameters (default: Earth orbiting Sun)
        m_central = float(params.get("central_mass", 1.989e30))  # kg (Sun)
        m_orbiting = float(params.get("orbiting_mass", 5.972e24))  # kg (Earth)
        r0 = float(params.get("semi_major_axis_m", 1.496e11))  # 1 AU in meters
        e = float(params.get("eccentricity", 0.0167))

        # Initial conditions at periapsis
        r_periapsis = r0 * (1.0 - e)
        v_periapsis = math.sqrt(self.G * m_central * (1.0 + e) / (r0 * (1.0 - e)))

        # Define 2D/3D ODE System: y = [x, y, vx, vy]
        def derivatives(t: float, y: np.ndarray) -> np.ndarray:
            rx, ry, vx, vy = y
            dist = math.sqrt(rx**2 + ry**2)
            if dist == 0:
                dist = 1e-5
            ax = -self.G * m_central * rx / (dist**3)
            ay = -self.G * m_central * ry / (dist**3)
            return np.array([vx, vy, ax, ay])

        period_seconds = 2.0 * math.pi * math.sqrt((r0**3) / (self.G * m_central))
        t_span = (0.0, period_seconds)
        t_eval = np.linspace(0.0, period_seconds, 100)

        y0 = [r_periapsis, 0.0, 0.0, v_periapsis]
        res = NumericalIDESolver.solve_ivp_system(derivatives, y0, t_span, t_eval)

        # Extract normalized 3D trajectory points for visual render
        scale = 10.0 / r0  # Scale down to 10 visual units
        trajectory_3d = []
        frames = []

        for idx in range(len(res["t"])):
            t_curr = res["t"][idx]
            rx = res["y"][0][idx]
            ry = res["y"][1][idx]
            vx = res["y"][2][idx]
            vy = res["y"][3][idx]

            x_norm = rx * scale
            y_norm = ry * scale
            trajectory_3d.append([round(x_norm, 4), round(y_norm, 4), 0.0])

            frames.append(
                SimulationFrame(
                    time=round(t_curr, 2),
                    objects=[
                        {"name": "central_body", "position": [0.0, 0.0, 0.0], "radius": 1.5, "color": "#FFCC00"},
                        {"name": "orbiting_body", "position": [x_norm, y_norm, 0.0], "radius": 0.5, "color": "#00F0FF"},
                    ],
                    telemetry={
                        "distance_m": math.sqrt(rx**2 + ry**2),
                        "velocity_m_s": math.sqrt(vx**2 + vy**2),
                    },
                )
            )

        self.result = SimulationResult(
            simulation_type="orbital_motion",
            domain="astronomy",
            summary={
                "orbital_period_days": round(period_seconds / 86400.0, 2),
                "semi_major_axis_km": round(r0 / 1000.0, 2),
                "eccentricity": e,
                "math_formula_used": "F_g = G * M * m / r^2",
            },
            data={
                "trajectoryPoints": trajectory_3d,
                "central_body": {"name": "Central Star", "color": "#FFCC00", "radius": 1.5},
                "orbiting_body": {"name": "Planet", "color": "#00F0FF", "radius": 0.5},
            },
            frames=frames,
        )
        return self.result

    def get_results(self) -> SimulationResult:
        return self.result if self.result else self.run()
