"""Pydantic models for physics simulations."""

from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectileSpec(BaseModel):
    initial_velocity: float = Field(default=20.0, gt=0, description="Initial velocity in m/s")
    launch_angle: float = Field(default=45.0, ge=0, le=90, description="Launch angle in degrees")
    initial_height: float = Field(default=0.0, ge=0, description="Initial height in meters")
    gravity: float = Field(default=9.81, gt=0, description="Acceleration due to gravity in m/s^2")
    time_step: float = Field(default=0.05, gt=0, description="Animation step size in seconds")


class PrismRefractionSpec(BaseModel):
    apex_angle: float = Field(default=60.0, gt=0, lt=180, description="Prism apex angle in degrees")
    refractive_index: float = Field(default=1.5, ge=1.0, le=3.0, description="Refractive index n")
    incident_angle: float = Field(default=30.0, ge=0, lt=90, description="Incident angle in degrees")


class PrismDispersionSpec(BaseModel):
    apex_angle: float = Field(default=60.0, gt=0, lt=180, description="Prism apex angle in degrees")
    incident_angle: float = Field(default=30.0, ge=0, lt=90, description="Incident angle in degrees")
    cauchy_b: float = Field(default=1.50, description="Cauchy B coefficient (base refractive index)")
    cauchy_c: float = Field(default=0.004, description="Cauchy C coefficient in um^2")
    wavelengths_nm: List[float] = Field(
        default_factory=lambda: [700.0, 620.0, 580.0, 530.0, 470.0, 420.0],
        description="Wavelengths in nanometers (Red to Violet)"
    )
