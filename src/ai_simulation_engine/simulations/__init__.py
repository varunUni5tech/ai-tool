"""Simulation package exports and automatic registration."""

from ai_simulation_engine.simulations.base import Simulation, StatelessSimulation
from ai_simulation_engine.simulations.registry import SimulationRegistry
from ai_simulation_engine.simulations.factory import SimulationFactory

# Import all simulations to ensure registry registration
from ai_simulation_engine.simulations.mathematics.function_sim import FunctionPlotSimulation
from ai_simulation_engine.simulations.physics.projectile_sim import ProjectileSimulation
from ai_simulation_engine.simulations.physics.prism_refraction_sim import PrismRefractionSimulation
from ai_simulation_engine.simulations.physics.prism_dispersion_sim import PrismDispersionSimulation
from ai_simulation_engine.simulations.astronomy.orbital_sim import OrbitalSimulation
from ai_simulation_engine.simulations.physics.shm_sim import SimpleHarmonicMotionSimulation
from ai_simulation_engine.simulations.engineering.control_system_sim import SecondOrderControlSystemSimulation

__all__ = [
    "Simulation",
    "StatelessSimulation",
    "SimulationRegistry",
    "SimulationFactory",
    "FunctionPlotSimulation",
    "ProjectileSimulation",
    "PrismRefractionSimulation",
    "PrismDispersionSimulation",
    "OrbitalSimulation",
    "SimpleHarmonicMotionSimulation",
    "SecondOrderControlSystemSimulation",
]

