"""Application configuration settings."""

from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Engine configuration settings loaded from environment or defaults."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Literal["development", "testing", "production"] = "development"
    port: int = 8000
    host: str = "0.0.0.0"
    log_level: str = "INFO"

    # AI Settings
    ai_provider: Literal["mock", "openai", "anthropic", "ollama"] = "mock"
    llm_provider: str = ""  # If set, overrides ai_provider for LLM_PROVIDER env var
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "qwen3"
    simulation_max_repair_attempts: int = 3

    @property
    def effective_ai_provider(self) -> str:
        return (self.llm_provider or self.ai_provider).lower()

    # Solver Defaults
    ode_solver_method: str = "RK45"
    solver_rtol: float = 1e-6
    solver_atol: float = 1e-8

    # Viz defaults
    default_figure_dpi: int = 150
    default_color_palette: str = "viridis"


settings = Settings()
