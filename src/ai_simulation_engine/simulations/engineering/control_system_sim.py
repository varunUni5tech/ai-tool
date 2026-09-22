"""Second Order Control System Step Response simulation planner."""

import math
import numpy as np
from typing import Dict, Any
from ai_simulation_engine.simulations.base import Simulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult, SimulationFrame


@SimulationRegistry.register("engineering", "second_order_control_system")
class SecondOrderControlSystemSimulation(Simulation):
    """Step response simulator for second-order linear dynamic systems G(s) = w_n^2 / (s^2 + 2*zeta*w_n*s + w_n^2)."""

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
        return {"type": "second_order_control_system", "parameters": self.spec.parameters}

    def run(self) -> SimulationResult:
        params = self.spec.parameters
        wn = float(params.get("omega_n", 5.0))  # Natural frequency (rad/s)
        zeta = float(params.get("zeta", 0.4))   # Damping ratio

        t_eval = np.linspace(0.0, 3.0, 150)
        response = []
        trajectory = []
        frames = []

        # Underdamped system (zeta < 1)
        if zeta < 1.0:
            wd = wn * math.sqrt(1.0 - zeta**2)
            phi = math.atan2(math.sqrt(1.0 - zeta**2), zeta)
            for t in t_eval:
                val = 1.0 - (math.exp(-zeta * wn * t) / math.sqrt(1.0 - zeta**2)) * math.sin(wd * t + phi)
                response.append(round(val, 4))
                trajectory.append([round(float(t), 3), round(val, 4), 0.0])
                frames.append(
                    SimulationFrame(
                        time=round(float(t), 3),
                        objects=[{"name": "step_response", "value": round(val, 4)}],
                    )
                )
            overshoot = math.exp(-zeta * math.pi / math.sqrt(1.0 - zeta**2)) * 100.0
            settling_time = 4.0 / (zeta * wn)
        else:
            # Overdamped/Critically damped fallback
            for t in t_eval:
                val = 1.0 - math.exp(-wn * t) * (1.0 + wn * t)
                response.append(round(val, 4))
                trajectory.append([round(float(t), 3), round(val, 4), 0.0])
                frames.append(
                    SimulationFrame(
                        time=round(float(t), 3),
                        objects=[{"name": "step_response", "value": round(val, 4)}],
                    )
                )
            overshoot = 0.0
            settling_time = 4.0 / wn

        self.result = SimulationResult(
            simulation_type="second_order_control_system",
            domain="engineering",
            summary={
                "natural_frequency_rad_s": wn,
                "damping_ratio": zeta,
                "peak_overshoot_percent": round(overshoot, 2),
                "settling_time_s": round(settling_time, 2),
                "transfer_function": "G(s) = w_n^2 / (s^2 + 2*zeta*w_n*s + w_n^2)",
            },
            data={
                "t": t_eval.tolist(),
                "response": response,
                "trajectoryPoints": trajectory,
            },
            frames=frames,
        )
        return self.result

    def get_results(self) -> SimulationResult:
        return self.result if self.result else self.run()
