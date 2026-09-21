"""Pydantic models for mathematics simulations."""

from typing import List, Optional
from pydantic import BaseModel, Field


class DomainInterval(BaseModel):
    min: float = 0.0
    max: float = 6.283185307179586  # 2*pi
    samples: int = Field(default=200, ge=10, le=10000)


class FunctionPlotSpec(BaseModel):
    expression: str = Field(description="Math expression using x, e.g. sin(x)")
    domain: DomainInterval = Field(default_factory=DomainInterval)
    parameters: dict = Field(default_factory=dict, description="Constant parameter substitutions")
