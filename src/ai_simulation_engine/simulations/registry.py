"""Simulation registry for dynamic lookup without if/elif dispatch."""

from typing import Dict, Type, Tuple, List
from ai_simulation_engine.simulations.base import Simulation
from ai_simulation_engine.errors.exceptions import UnsupportedSimulationError


class SimulationRegistry:
    """Registry mapping (domain, simulation_type) to Simulation classes."""

    _registry: Dict[Tuple[str, str], Type[Simulation]] = {}

    @classmethod
    def register(cls, domain: str, simulation_type: str):
        """Decorator or method to register a simulation class."""
        def decorator(sim_cls: Type[Simulation]):
            key = (domain.lower(), simulation_type.lower())
            cls._registry[key] = sim_cls
            return sim_cls
        return decorator

    @classmethod
    def get(cls, domain: str, simulation_type: str) -> Type[Simulation]:
        """Retrieve registered simulation class."""
        key = (domain.lower(), simulation_type.lower())
        if key not in cls._registry:
            # Also allow fallback search by type alone if domain matches
            for (reg_domain, reg_type), sim_cls in cls._registry.items():
                if reg_type == simulation_type.lower():
                    return sim_cls
            raise UnsupportedSimulationError(
                f"Simulation domain='{domain}', type='{simulation_type}' is not registered. "
                f"Available simulations: {cls.list_registered()}"
            )
        return cls._registry[key]

    @classmethod
    def list_registered(cls) -> List[Dict[str, str]]:
        """List all currently registered simulations."""
        return [
            {"domain": domain, "simulation_type": sim_type, "class": sim_cls.__name__}
            for (domain, sim_type), sim_cls in cls._registry.items()
        ]
