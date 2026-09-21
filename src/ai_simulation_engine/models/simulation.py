"""Core engine-agnostic Pydantic models for simulation specs and outputs."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from ai_simulation_engine.models.visualization import VisualizationConfig


class EducationalMeta(BaseModel):
    subject: str = "Physics/Mathematics"
    chapter: Optional[str] = None
    topic: Optional[str] = None
    difficulty: str = "Introductory"


class ObjectSpec(BaseModel):
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class SimulationSpec(BaseModel):
    simulation_schema_version: str = "1.0"
    simulation_type: str = Field(description="Name of registered simulation")
    domain: str = Field(description="Domain name e.g. mathematics, mechanics, optics")
    objects: List[ObjectSpec] = Field(default_factory=list)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    educational: Optional[EducationalMeta] = None


class SimulationFrame(BaseModel):
    time: float
    objects: List[Dict[str, Any]]
    telemetry: Dict[str, Any] = Field(default_factory=dict)


class SimulationResult(BaseModel):
    simulation_type: str
    domain: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    summary: Dict[str, Any] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)
    frames: List[SimulationFrame] = Field(default_factory=list)
