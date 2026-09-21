"""AI Orchestration Service."""

from typing import Dict, Any
from ai_simulation_engine.ai.providers.factory import AIProviderFactory
from ai_simulation_engine.schemas.simulation import validate_spec_dict
from ai_simulation_engine.models.simulation import SimulationSpec


class AIService:
    """Service to handle Natural Language -> Validated SimulationSpec processing."""

    @staticmethod
    def generate_spec_from_prompt(prompt: str, provider_name: str = None) -> SimulationSpec:
        provider = AIProviderFactory.get_provider(provider_name)
        raw_spec_dict = provider.generate_spec(prompt)
        validated_spec = validate_spec_dict(raw_spec_dict)
        return validated_spec
