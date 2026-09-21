"""Visualization Service."""

from ai_simulation_engine.models.simulation import SimulationResult
from ai_simulation_engine.visualization.plots_2d.matplotlib_backend import MatplotlibExporter


class VisualizationService:
    """Service to export simulation results to image graphics."""

    @staticmethod
    def render_result(result: SimulationResult, output_path: str = "outputs/render.png") -> str:
        return MatplotlibExporter.render_to_file(result, output_path)
