"""Abstract base class for AI specification generation providers."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class AIProvider(ABC):
    """Abstract interface for AI specification generator providers."""

    @abstractmethod
    def generate_spec(self, prompt: str) -> Dict[str, Any]:
        """Convert natural language request string into a structured JSON simulation spec dict."""
        pass
