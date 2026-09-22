"""Unit tests for OrbitalMotionSimulation planner."""

import pytest
from ai_simulation_engine.models.simulation import SimulationSpec
from ai_simulation_engine.simulations.astronomy.orbital_sim import OrbitalSimulation


def test_orbital_simulation_execution():
    spec = SimulationSpec(
        simulation_type="orbital_motion",
        domain="astronomy",
        parameters={
            "central_mass": 1.989e30,
            "orbiting_mass": 5.972e24,
            "semi_major_axis_m": 1.496e11,
            "eccentricity": 0.0167,
        },
    )
    sim = OrbitalSimulation(spec)
    result = sim.run()

    assert result.simulation_type == "orbital_motion"
    assert result.domain == "astronomy"
    assert "trajectoryPoints" in result.data
    assert len(result.data["trajectoryPoints"]) >= 100
    assert result.summary["planets_count"] >= 1
