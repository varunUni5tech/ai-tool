"""Custom exception hierarchy for the simulation engine."""


class SimulationEngineError(Exception):
    """Base exception for all engine errors."""

    pass


class SimulationValidationError(SimulationEngineError):
    """Raised when simulation spec fails schema or Pydantic validation."""

    pass


class UnsupportedSimulationError(SimulationEngineError):
    """Raised when requested simulation is not registered."""

    pass


class UnsafeExpressionError(SimulationEngineError):
    """Raised when math expression parsing fails safety checks."""

    pass


class SolverError(SimulationEngineError):
    """Raised when numerical or symbolic solver fails."""

    pass


class AIParsingError(SimulationEngineError):
    """Raised when LLM output cannot be parsed into valid simulation spec."""

    pass


class VisualizationError(SimulationEngineError):
    """Raised when rendering output fails."""

    pass
