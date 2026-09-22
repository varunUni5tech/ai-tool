"""AI Provider Factory."""

from ai_simulation_engine.ai.providers.base import AIProvider
from ai_simulation_engine.ai.providers.mock import MockAIProvider
from ai_simulation_engine.ai.providers.openai_provider import OpenAIProvider
from ai_simulation_engine.ai.providers.ollama_provider import OllamaProvider
from ai_simulation_engine.config.settings import settings


class AIProviderFactory:
    """Factory to instantiate configured AI provider."""

    @staticmethod
    def get_provider(name: str = None) -> AIProvider:
        provider_name = (name or settings.ai_provider).lower()
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "ollama":
            return OllamaProvider(host_url=settings.ollama_host, model_name=settings.ollama_model)
        # Default fallback to mock provider
        return MockAIProvider()

