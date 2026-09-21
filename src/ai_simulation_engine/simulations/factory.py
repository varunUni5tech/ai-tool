"""Factory for creating and initializing simulation instances from specs."""

from ai_simulation_engine.models.simulation import SimulationSpec
from ai_simulation_engine.simulations.base import Simulation
from ai_simulation_engine.simulations.registry import SimulationRegistry


class SimulationFactory:
    """Factory to build initialized simulation objects from validated SimulationSpec."""

    @staticmethod
    def create(spec: SimulationSpec) -> Simulation:
        sim_class = SimulationRegistry.get(spec.domain, spec.simulation_type)
        instance = sim_class(spec)
        instance.validate()
        instance.initialize()
        return instance
