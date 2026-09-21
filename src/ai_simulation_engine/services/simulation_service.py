"""Simulation Execution Service."""

from ai_simulation_engine.models.simulation import SimulationSpec, SimulationResult
from ai_simulation_engine.simulations.factory import SimulationFactory


class SimulationService:
    """Service to orchestrate simulation execution from validated spec."""

    @staticmethod
    def execute_simulation(spec: SimulationSpec) -> SimulationResult:
        sim_instance = SimulationFactory.create(spec)
        result = sim_instance.run()
        return result
