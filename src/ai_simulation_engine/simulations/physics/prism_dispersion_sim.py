"""Physics simulation: Prism Spectral Dispersion."""

import math
from typing import Dict, Any, List
from ai_simulation_engine.simulations.base import StatelessSimulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult
from ai_simulation_engine.models.physics import PrismDispersionSpec
from ai_simulation_engine.simulations.physics.prism_refraction_sim import PrismRefractionSimulation
from ai_simulation_engine.errors.exceptions import SimulationValidationError


@SimulationRegistry.register(domain="optics", simulation_type="prism_dispersion")
class PrismDispersionSimulation(StatelessSimulation):
    """Computes spectral dispersion of white light into constituent colors using Cauchy's Equation."""

    def __init__(self, spec: SimulationSpec):
        super().__init__(spec)
        self.params: PrismDispersionSpec = None
        self.refraction_sim: PrismRefractionSimulation = None
        self.result: SimulationResult = None

    def validate(self) -> None:
        try:
            self.params = PrismDispersionSpec.model_validate(self.spec.parameters)
        except Exception as e:
            raise SimulationValidationError(f"Invalid PrismDispersionSpec parameters: {str(e)}") from e

    def initialize(self) -> None:
        dummy_spec = SimulationSpec(
            simulation_type="optical_prism",
            domain="optics",
            parameters={
                "apex_angle": self.params.apex_angle,
                "refractive_index": self.params.cauchy_b,
                "incident_angle": self.params.incident_angle,
            }
        )
        self.refraction_sim = PrismRefractionSimulation(dummy_spec)
        self.refraction_sim.validate()
        self.refraction_sim.initialize()
        self.initialized = True

    def cauchy_refractive_index(self, wavelength_nm: float) -> float:
        """Cauchy equation: n(lambda) = B + C / lambda_um^2."""
        lambda_um = wavelength_nm / 1000.0  # convert nm to micrometers
        return self.params.cauchy_b + (self.params.cauchy_c / (lambda_um**2))

    def nm_to_hex_color(self, wavelength_nm: float) -> str:
        """Map wavelength in nm to approximate HEX spectral color."""
        if wavelength_nm >= 620:
            return "#FF0000"  # Red
        elif wavelength_nm >= 590:
            return "#FF7F00"  # Orange
        elif wavelength_nm >= 570:
            return "#FFFF00"  # Yellow
        elif wavelength_nm >= 495:
            return "#00FF00"  # Green
        elif wavelength_nm >= 450:
            return "#0000FF"  # Blue
        elif wavelength_nm >= 400:
            return "#8B00FF"  # Violet
        return "#FFFFFF"

    def run(self) -> SimulationResult:
        if not self.initialized:
            self.initialize()

        spectral_results = []
        deviations = []

        for wl in sorted(self.params.wavelengths_nm, reverse=True):  # Red to Violet
            n_wl = self.cauchy_refractive_index(wl)
            ray_info = self.refraction_sim.calculate_ray_path(
                i1_deg=self.params.incident_angle,
                n=n_wl,
                A_deg=self.params.apex_angle,
            )
            color_hex = self.nm_to_hex_color(wl)
            ray_info["wavelength_nm"] = wl
            ray_info["refractive_index"] = float(round(n_wl, 5))
            ray_info["color"] = color_hex
            spectral_results.append(ray_info)

            if ray_info["deviation_deg"] is not None:
                deviations.append(ray_info["deviation_deg"])

        angular_dispersion = (max(deviations) - min(deviations)) if len(deviations) > 1 else 0.0

        summary = {
            "apex_angle_deg": self.params.apex_angle,
            "incident_angle_deg": self.params.incident_angle,
            "cauchy_b": self.params.cauchy_b,
            "cauchy_c": self.params.cauchy_c,
            "wavelengths_count": len(self.params.wavelengths_nm),
            "min_deviation_deg": float(round(min(deviations), 4)) if deviations else None,
            "max_deviation_deg": float(round(max(deviations), 4)) if deviations else None,
            "angular_dispersion_deg": float(round(angular_dispersion, 4)),
        }

        self.result = SimulationResult(
            simulation_type=self.spec.simulation_type,
            domain=self.spec.domain,
            metadata={"params": self.params.model_dump()},
            summary=summary,
            data={"spectral_rays": spectral_results},
            frames=[],
        )
        return self.result

    def get_results(self) -> SimulationResult:
        if self.result is None:
            return self.run()
        return self.result
