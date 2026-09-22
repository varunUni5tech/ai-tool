"""Visualization router converting raw numerical simulation results into target visual formats."""

from typing import Dict, Any
from ai_simulation_engine.models.simulation import SimulationResult
from ai_simulation_engine.schemas.universal_v2 import UniversalSimulationSpec


class VisualizationRouter:
    """Decoupled router generating rendering payloads from simulation data."""

    @staticmethod
    def render_payload(
        result: SimulationResult,
        spec: UniversalSimulationSpec,
        output_format: str = "json",
    ) -> Dict[str, Any]:
        """Format simulation result and spec into visualization data."""
        edu_level = spec.education.level if spec and spec.education else "high_school"
        viz_type = spec.visualization.type if spec and spec.visualization else "2d_plot"

        # Formulate presentation annotations based on educational level
        show_formulas = edu_level in ["high_school", "undergraduate", "engineering"]
        show_derivations = edu_level in ["undergraduate", "engineering"]

        return {
            "simulation_type": result.simulation_type,
            "domain": result.domain,
            "visualization_type": viz_type,
            "educational_level": edu_level,
            "summary": result.summary,
            "presentation": {
                "show_formulas": show_formulas,
                "show_derivations": show_derivations,
                "title": result.summary.get("math_formula_used", result.simulation_type),
            },
            "data": result.data,
            "frames": [f.model_dump() for f in result.frames],
        }
