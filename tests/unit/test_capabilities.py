"""Unit tests for capability registry and system prompt generation."""

import pytest
from ai_simulation_engine.simulations.capabilities import CapabilityRegistry
from ai_simulation_engine.ai.prompts.system_prompt import get_system_prompt


def test_capability_registry():
    capabilities = CapabilityRegistry.list_all()
    assert len(capabilities) >= 5

    orbital = CapabilityRegistry.get("orbital_motion")
    assert orbital is not None
    assert orbital.domain == "astronomy"
    assert "semi_major_axis_m" in orbital.required_parameters


def test_system_prompt_generation():
    prompt = get_system_prompt()
    assert "SUPPORTED SIMULATION CAPABILITIES AND SCHEMAS" in prompt
    assert "orbital_motion" in prompt
    assert "projectile_motion" in prompt
