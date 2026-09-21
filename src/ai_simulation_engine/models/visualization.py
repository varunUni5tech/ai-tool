"""Pydantic models for visualization parameters."""

from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class VisualizationType(str, Enum):
    FUNCTION_PLOT = "function_plot"
    TRAJECTORY_2D = "trajectory_2d"
    RAY_DIAGRAM = "ray_diagram"
    DISPERSION_SPECTRUM = "dispersion_spectrum"
    RAY_DIAGRAM_3D = "ray_diagram_3d"
    DISPERSION_3D = "dispersion_3d"


class VisualizationConfig(BaseModel):
    type: VisualizationType = VisualizationType.FUNCTION_PLOT
    animated: bool = False
    title: Optional[str] = None
    x_label: Optional[str] = None
    y_label: Optional[str] = None
    show_grid: bool = True
    color_palette: str = "viridis"
    options: Dict[str, Any] = Field(default_factory=dict)
