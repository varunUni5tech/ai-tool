"""Abstract Base Classes for all simulations."""

from abc import ABC, abstractmethod
from typing import Dict, Any
from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult


class Simulation(ABC):
    """Abstract base class for all dynamic and stateful simulations."""

    def __init__(self, spec: SimulationSpec):
        self.spec = spec
        self.initialized = False

    @abstractmethod
    def validate(self) -> None:
        """Validate spec parameters specific to this simulation."""
        pass

    @abstractmethod
    def initialize(self) -> None:
        """Initialize initial state and solver conditions."""
        pass

    @abstractmethod
    def step(self, dt: float) -> None:
        """Advance state by delta time dt."""
        pass

    @abstractmethod
    def run(self) -> SimulationResult:
        """Execute full simulation and return standardized result object."""
        pass

    @abstractmethod
    def get_state(self) -> Dict[str, Any]:
        """Get current instantaneous simulation state snapshot."""
        pass

    @abstractmethod
    def get_results(self) -> SimulationResult:
        """Get final computed simulation results."""
        pass


class StatelessSimulation(Simulation):
    """Base class for static/stateless simulations (e.g., function plotting, optics ray traces)."""

    def step(self, dt: float) -> None:
        """Stateless simulations do not time-step."""
        pass

    def get_state(self) -> Dict[str, Any]:
        """Stateless snapshot returns current static parameters."""
        return {"type": "stateless", "parameters": self.spec.parameters}
