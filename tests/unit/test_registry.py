"""Unit tests for Simulation Registry and Factory."""

import pytest
import ai_simulation_engine.simulations  # noqa: F401
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.simulations.factory import SimulationFactory
from ai_simulation_engine.models.simulation import SimulationSpec
from ai_simulation_engine.errors.exceptions import UnsupportedSimulationError


def test_registry_lookup():
    cls = SimulationRegistry.get("mechanics", "projectile_motion")
    assert cls is not None


def test_registry_unsupported_error():
    with pytest.raises(UnsupportedSimulationError):
        SimulationRegistry.get("quantum", "non_existent_sim")


def test_factory_creation():
    spec = SimulationSpec(
        simulation_type="function_plot",
        domain="mathematics",
        parameters={"expression": "cos(x)"},
    )
    sim = SimulationFactory.create(spec)
    res = sim.run()
    assert res.summary["expression"] == "cos(x)"
