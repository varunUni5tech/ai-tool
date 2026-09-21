"""SciPy ODE solver wrapper for physics numerical integration."""

from typing import Callable, Tuple, List, Dict, Any
import numpy as np
from scipy.integrate import solve_ivp
from ai_simulation_engine.errors.exceptions import SolverError
from ai_simulation_engine.config.settings import settings


class ODESolver:
    """Wrapper around scipy.integrate.solve_ivp."""

    @staticmethod
    def solve(
        fun: Callable[[float, np.ndarray], np.ndarray],
        t_span: Tuple[float, float],
        y0: List[float],
        t_eval: np.ndarray = None,
        method: str = None,
    ) -> Dict[str, Any]:
        solver_method = method or settings.ode_solver_method
        try:
            sol = solve_ivp(
                fun=fun,
                t_span=t_span,
                y0=y0,
                t_eval=t_eval,
                method=solver_method,
                rtol=settings.solver_rtol,
                atol=settings.solver_atol,
            )
            if not sol.success:
                raise SolverError(f"ODE integration failed: {sol.message}")
            return {
                "t": sol.t.tolist(),
                "y": sol.y.tolist(),
                "success": sol.success,
            }
        except Exception as e:
            if isinstance(e, SolverError):
                raise
            raise SolverError(f"Error executing ODE solver: {str(e)}") from e
