"""Simple Harmonic Motion (SHM) simulation planner."""

import math
import numpy as np
from typing import Dict, Any
from ai_simulation_engine.simulations.base import Simulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult, SimulationFrame


@SimulationRegistry.register("mechanics", "simple_harmonic_motion")
class SimpleHarmonicMotionSimulation(Simulation):
    """Mass-Spring Simple Harmonic Motion simulator."""

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
        return {"type": "simple_harmonic_motion", "parameters": self.spec.parameters}

    def run(self) -> SimulationResult:
        params = self.spec.parameters
        mass = float(params.get("mass", 1.0))
        k = float(params.get("spring_constant", 10.0))
        x0 = float(params.get("initial_displacement", 1.0))
        v0 = float(params.get("initial_velocity", 0.0))

        omega = math.sqrt(k / mass)
        period = 2.0 * math.pi / omega

        t_eval = np.linspace(0.0, 2.0 * period, 100)
        positions = []
        velocities = []
        trajectory = []
        frames = []

        for t in t_eval:
            x_t = x0 * math.cos(omega * t) + (v0 / omega) * math.sin(omega * t)
            v_t = -x0 * omega * math.sin(omega * t) + v0 * math.cos(omega * t)

            positions.append(round(x_t, 4))
            velocities.append(round(v_t, 4))
            trajectory.append([round(x_t, 4), 0.0, 0.0])

            frames.append(
                SimulationFrame(
                    time=round(float(t), 2),
                    objects=[{"name": "mass", "position": [round(x_t, 4), 0.0, 0.0]}],
                    telemetry={"displacement_m": round(x_t, 4), "velocity_m_s": round(v_t, 4)},
                )
            )

        self.result = SimulationResult(
            simulation_type="simple_harmonic_motion",
            domain="mechanics",
            summary={
                "angular_frequency_rad_s": round(omega, 4),
                "period_s": round(period, 4),
                "math_formula_used": "x(t) = A * cos(omega * t + phi)",
            },
            data={
                "t": t_eval.tolist(),
                "x": positions,
                "v": velocities,
                "trajectoryPoints": trajectory,
            },
            frames=frames,
        )
        return self.result

    def get_results(self) -> SimulationResult:
        return self.result if self.result else self.run()
