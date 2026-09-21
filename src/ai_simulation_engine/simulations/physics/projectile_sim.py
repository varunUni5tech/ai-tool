"""Physics simulation: Projectile Motion."""

import math
import numpy as np
from typing import Dict, Any, List
from ai_simulation_engine.simulations.base import Simulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult, SimulationFrame
from ai_simulation_engine.models.physics import ProjectileSpec
from ai_simulation_engine.errors.exceptions import SimulationValidationError
from ai_simulation_engine.solvers.ode.scipy_solver import ODESolver


@SimulationRegistry.register(domain="mechanics", simulation_type="projectile_motion")
class ProjectileSimulation(Simulation):
    """Computes 2D projectile motion under gravity using analytical and ODE numerical integration."""

    def __init__(self, spec: SimulationSpec):
        super().__init__(spec)
        self.params: ProjectileSpec = None
        self.v0x: float = 0.0
        self.v0y: float = 0.0
        self.flight_time: float = 0.0
        self.max_height: float = 0.0
        self.range_dist: float = 0.0
        self.frames: List[SimulationFrame] = []
        self.result: SimulationResult = None

    def validate(self) -> None:
        try:
            self.params = ProjectileSpec.model_validate(self.spec.parameters)
        except Exception as e:
            raise SimulationValidationError(f"Invalid ProjectileSpec parameters: {str(e)}") from e

    def initialize(self) -> None:
        rad = math.radians(self.params.launch_angle)
        self.v0x = self.params.initial_velocity * math.cos(rad)
        self.v0y = self.params.initial_velocity * math.sin(rad)
        g = self.params.gravity
        h0 = self.params.initial_height

        # Calculate theoretical flight time: h(t) = h0 + v0y*t - 0.5*g*t^2 = 0
        # Quadratic formula: 0.5*g*t^2 - v0y*t - h0 = 0
        discriminant = self.v0y**2 + 2 * g * h0
        self.flight_time = (self.v0y + math.sqrt(discriminant)) / g
        self.max_height = h0 + (self.v0y**2) / (2 * g)
        self.range_dist = self.v0x * self.flight_time
        self.initialized = True

    def step(self, dt: float) -> None:
        pass

    def run(self) -> SimulationResult:
        if not self.initialized:
            self.initialize()

        g = self.params.gravity
        dt = self.params.time_step
        t_eval = np.arange(0, self.flight_time, dt)
        if len(t_eval) == 0 or t_eval[-1] < self.flight_time:
            t_eval = np.append(t_eval, self.flight_time)
        t_eval = t_eval[t_eval <= self.flight_time]

        # ODE system state: state = [x, y, vx, vy]
        def projectile_ode(t, state):
            x, y, vx, vy = state
            return [vx, vy, 0.0, -g]

        y0 = [0.0, self.params.initial_height, self.v0x, self.v0y]
        ode_res = ODESolver.solve(
            fun=projectile_ode,
            t_span=(0, self.flight_time),
            y0=y0,
            t_eval=t_eval,
        )

        t_series = ode_res["t"]
        x_series = ode_res["y"][0]
        y_series = [max(0.0, val) for val in ode_res["y"][1]]
        vx_series = ode_res["y"][2]
        vy_series = ode_res["y"][3]

        self.frames = []
        for i in range(len(t_series)):
            t_val = t_series[i]
            frame = SimulationFrame(
                time=float(round(t_val, 4)),
                objects=[
                    {
                        "id": "projectile",
                        "position": [float(x_series[i]), float(y_series[i])],
                        "velocity": [float(vx_series[i]), float(vy_series[i])],
                        "speed": float(math.hypot(vx_series[i], vy_series[i])),
                    }
                ],
                telemetry={
                    "height": float(y_series[i]),
                    "distance": float(x_series[i]),
                },
            )
            self.frames.append(frame)

        summary = {
            "initial_velocity": self.params.initial_velocity,
            "launch_angle_deg": self.params.launch_angle,
            "initial_height": self.params.initial_height,
            "gravity": self.params.gravity,
            "flight_time_s": float(round(self.flight_time, 4)),
            "max_height_m": float(round(self.max_height, 4)),
            "horizontal_range_m": float(round(self.range_dist, 4)),
        }

        data = {
            "time": t_series,
            "x": x_series,
            "y": y_series,
            "vx": vx_series,
            "vy": vy_series,
        }

        self.result = SimulationResult(
            simulation_type=self.spec.simulation_type,
            domain=self.spec.domain,
            metadata={"params": self.params.model_dump()},
            summary=summary,
            data=data,
            frames=self.frames,
        )
        return self.result

    def get_state(self) -> Dict[str, Any]:
        if self.frames:
            return self.frames[-1].model_dump()
        return {"flight_time": self.flight_time, "max_height": self.max_height}

    def get_results(self) -> SimulationResult:
        if self.result is None:
            return self.run()
        return self.result
