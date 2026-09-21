"""Logging setup for the simulation engine."""

import logging
import sys
from ai_simulation_engine.config.settings import settings


def setup_logging():
    """Configure structured logging for backend API and engine components."""
    log_format = (
        "\033[36m%(asctime)s\033[0m | "
        "\033[32m%(levelname)-8s\033[0m | "
        "\033[35m%(name)s\033[0m - "
        "\033[37m%(message)s\033[0m"
    )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set logger level for simulation components
    logger = logging.getLogger("ai_simulation_engine")
    logger.setLevel(logging.INFO)
    return logger


logger = setup_logging()
