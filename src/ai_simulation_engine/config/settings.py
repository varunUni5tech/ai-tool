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
    ai_provider: Literal["mock", "openai", "anthropic"] = "mock"
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Solver Defaults
    ode_solver_method: str = "RK45"
    solver_rtol: float = 1e-6
    solver_atol: float = 1e-8

    # Viz defaults
    default_figure_dpi: int = 150
    default_color_palette: str = "viridis"


settings = Settings()
