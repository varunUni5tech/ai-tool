"""Unit tests for Universal Simulation Spec 2.0."""

import pytest
from ai_simulation_engine.schemas.universal_v2 import UniversalSimulationSpec, SimulationMeta


def test_universal_spec_validation():
    data = {
        "schema_version": "2.0",
        "simulation": {
            "type": "orbital_motion",
            "domain": "astronomy",
            "title": "Earth Orbiting Sun",
            "dimension": "3d",
        },
        "parameters": {"semi_major_axis_m": 1.496e11},
    }
    spec = UniversalSimulationSpec.model_validate(data)
    assert spec.schema_version == "2.0"
    assert spec.simulation.type == "orbital_motion"
    assert spec.simulation.domain == "astronomy"
    assert spec.parameters["semi_major_axis_m"] == 1.496e11


def test_v1_to_v2_spec_migration():
    v1_data = {
        "simulation_type": "projectile_motion",
        "domain": "mechanics",
        "parameters": {"initial_velocity": 20.0, "launch_angle": 45.0},
        "visualization": {"type": "trajectory_2d"},
    }
    spec_v2 = UniversalSimulationSpec.from_v1_dict(v1_data)
    assert spec_v2.schema_version == "2.0"
    assert spec_v2.simulation.type == "projectile_motion"
    assert spec_v2.parameters["initial_velocity"] == 20.0
