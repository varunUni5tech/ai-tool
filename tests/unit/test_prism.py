"""Unit tests for Prism Refraction and Dispersion simulations."""

import pytest
from ai_simulation_engine.models.simulation import SimulationSpec
from ai_simulation_engine.simulations.physics.prism_refraction_sim import PrismRefractionSimulation
from ai_simulation_engine.simulations.physics.prism_dispersion_sim import PrismDispersionSimulation


def test_prism_refraction():
    spec = SimulationSpec(
        simulation_type="optical_prism",
        domain="optics",
        parameters={
            "apex_angle": 60.0,
            "refractive_index": 1.5,
            "incident_angle": 30.0,
        }
    )
    sim = PrismRefractionSimulation(spec)
    sim.validate()
    sim.initialize()
    res = sim.run()

    assert res.summary["total_internal_reflection"] is False
    assert res.summary["refracted_angle_1_deg"] is not None
    assert res.summary["deviation_angle_deg"] is not None


def test_prism_dispersion():
    spec = SimulationSpec(
        simulation_type="prism_dispersion",
        domain="optics",
        parameters={
            "apex_angle": 60.0,
            "incident_angle": 30.0,
            "cauchy_b": 1.5,
            "cauchy_c": 0.004,
            "wavelengths_nm": [700.0, 400.0],
        }
    )
    sim = PrismDispersionSimulation(spec)
    sim.validate()
    sim.initialize()
    res = sim.run()

    # Violet (400nm) has higher n and should deviate more than Red (700nm)
    assert res.summary["angular_dispersion_deg"] > 0.0
    assert len(res.data["spectral_rays"]) == 2
