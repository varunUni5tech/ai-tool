"""Mathematics simulation: Function Plotting."""

import numpy as np
from typing import Dict, Any
from ai_simulation_engine.simulations.base import StatelessSimulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult
from ai_simulation_engine.models.mathematics import FunctionPlotSpec
from ai_simulation_engine.math_engine.expression.evaluator import SafeExpressionEvaluator
from ai_simulation_engine.errors.exceptions import SimulationValidationError


@SimulationRegistry.register(domain="mathematics", simulation_type="function_plot")
class FunctionPlotSimulation(StatelessSimulation):
    """Evaluates mathematical expression y = f(x) over a grid."""

    def __init__(self, spec: SimulationSpec):
        super().__init__(spec)
        self.plot_spec: FunctionPlotSpec = None
        self.x_vals: np.ndarray = None
        self.y_vals: np.ndarray = None
        self.result: SimulationResult = None

    def validate(self) -> None:
        try:
            self.plot_spec = FunctionPlotSpec.model_validate(self.spec.parameters)
        except Exception as e:
            raise SimulationValidationError(f"Invalid FunctionPlotSpec parameters: {str(e)}") from e

    def initialize(self) -> None:
        grid_spec = self.plot_spec.domain
        self.x_vals = np.linspace(grid_spec.min, grid_spec.max, grid_spec.samples)
        self.initialized = True

    def run(self) -> SimulationResult:
        if not self.initialized:
            self.initialize()

        evaluator = SafeExpressionEvaluator(self.plot_spec.expression, var_name="x")
        self.y_vals = evaluator.evaluate_grid(self.x_vals)

        # Basic numerical analysis (min, max, mean)
        min_idx = int(np.argmin(self.y_vals))
        max_idx = int(np.argmax(self.y_vals))

        summary = {
            "expression": self.plot_spec.expression,
            "domain_min": self.plot_spec.domain.min,
            "domain_max": self.plot_spec.domain.max,
            "samples": len(self.x_vals),
            "y_min": float(self.y_vals[min_idx]),
            "x_at_y_min": float(self.x_vals[min_idx]),
            "y_max": float(self.y_vals[max_idx]),
            "x_at_y_max": float(self.x_vals[max_idx]),
            "y_mean": float(np.mean(self.y_vals)),
        }

        data = {
            "x": self.x_vals.tolist(),
            "y": self.y_vals.tolist(),
        }

        self.result = SimulationResult(
            simulation_type=self.spec.simulation_type,
            domain=self.spec.domain,
            metadata={"expression": self.plot_spec.expression},
            summary=summary,
            data=data,
            frames=[],
        )
        return self.result

    def get_results(self) -> SimulationResult:
        if self.result is None:
            return self.run()
        return self.result
