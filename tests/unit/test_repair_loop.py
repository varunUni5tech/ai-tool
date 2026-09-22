"""Unit tests for automatic LLM validation repair loop."""

import pytest
from ai_simulation_engine.ai.providers.base import AIProvider
from ai_simulation_engine.ai.repair_loop import validate_and_repair_spec
from ai_simulation_engine.errors.exceptions import SimulationValidationError


class FailingMockProvider(AIProvider):
    """Mock provider that returns invalid JSON twice before returning a valid spec."""

    def __init__(self):
        self.calls = 0

    def generate_spec(self, prompt: str):
        self.calls += 1
        if self.calls == 1:
            return "NOT VALID JSON"
        elif self.calls == 2:
            return {"schema_version": "2.0", "simulation": {"invalid": True}}
        return {
            "schema_version": "2.0",
            "simulation": {"type": "orbital_motion", "domain": "astronomy"},
            "parameters": {"semi_major_axis_m": 1.496e11},
        }


def test_repair_loop_recovery():
    provider = FailingMockProvider()
    spec, repairs = validate_and_repair_spec(provider, "Show Earth orbiting Sun", max_repair_attempts=3)
    assert repairs == 2
    assert spec.simulation.type == "orbital_motion"
    assert provider.calls == 3


def test_repair_loop_exceeds_max_attempts():
    class AlwaysFailingProvider(AIProvider):
        def generate_spec(self, prompt: str):
            return "INVALID JSON ALWAYS"

    provider = AlwaysFailingProvider()
    with pytest.raises(SimulationValidationError):
        validate_and_repair_spec(provider, "Invalid test", max_repair_attempts=2)
