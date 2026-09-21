"""Unit tests for Projectile Motion simulation."""

import math
import pytest
from ai_simulation_engine.models.simulation import SimulationSpec
from ai_simulation_engine.simulations.physics.projectile_sim import ProjectileSimulation


def test_projectile_kinematics():
    spec = SimulationSpec(
        simulation_type="projectile_motion",
        domain="mechanics",
        parameters={
            "initial_velocity": 20.0,
            "launch_angle": 45.0,
            "initial_height": 0.0,
            "gravity": 9.81,
            "time_step": 0.05,
        }
    )

    sim = ProjectileSimulation(spec)
    sim.validate()
    sim.initialize()
    res = sim.run()

    # Theoretical maximum height: (v0*sin(45))^2 / (2*g) = (20 * 0.7071)^2 / 19.62 = 10.1936 m
    expected_max_h = (20.0 * math.sin(math.radians(45))) ** 2 / (2 * 9.81)
    assert pytest.approx(res.summary["max_height_m"], rel=1e-2) == expected_max_h

    # Theoretical flight time: 2 * v0 * sin(45) / g = 2 * 14.142 / 9.81 = 2.883 s
    expected_time = 2 * 20.0 * math.sin(math.radians(45)) / 9.81
    assert pytest.approx(res.summary["flight_time_s"], rel=1e-2) == expected_time

    assert len(res.frames) > 0
