"""Numerical ODE Solver implementation wrapping scipy.integrate.solve_ivp."""

import numpy as np
from scipy.integrate import solve_ivp
from typing import Callable, Dict, Any, List, Tuple


class NumericalIDESolver:
    """Deterministic SciPy IVP numerical integrator for physical systems."""

    @staticmethod
    def solve_ivp_system(
        derivatives_fn: Callable[[float, np.ndarray], np.ndarray],
        y0: List[float],
        t_span: Tuple[float, float],
        t_eval: np.ndarray,
        method: str = "RK45",
        rtol: float = 1e-6,
        atol: float = 1e-8,
    ) -> Dict[str, Any]:
        """Execute SciPy ODE integration."""
        sol = solve_ivp(
            fun=derivatives_fn,
            t_span=t_span,
            y0=y0,
            t_eval=t_eval,
            method=method,
            rtol=rtol,
            atol=atol,
        )
        return {
            "success": sol.success,
            "t": sol.t.tolist(),
            "y": sol.y.tolist(),
            "message": sol.message,
        }
