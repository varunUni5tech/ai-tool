"""Vectorized numerical evaluator for parsed SymPy expressions."""

import sympy as sp
import numpy as np
from typing import Dict, Any
from ai_simulation_engine.math_engine.expression.parser import SafeExpressionParser
from ai_simulation_engine.errors.exceptions import UnsafeExpressionError


class SafeExpressionEvaluator:
    """Evaluates SymPy expressions over NumPy arrays numerically."""

    def __init__(self, expr_str: str, var_name: str = "x"):
        self.var_name = var_name
        self.parser = SafeExpressionParser(allowed_variables={var_name})
        self.parsed_expr = self.parser.parse(expr_str)
        var_symbol = sp.Symbol(var_name)

        # Create fast vectorized function via sympy lambdify using numpy module
        try:
            self.vectorized_func = sp.lambdify(var_symbol, self.parsed_expr, modules=["numpy"])
        except Exception as e:
            raise UnsafeExpressionError(f"Failed to lambdify expression: {str(e)}") from e

    def evaluate_grid(self, x_values: np.ndarray) -> np.ndarray:
        """Evaluate expression over a NumPy array."""
        try:
            res = self.vectorized_func(x_values)
            # Handle constant outputs scalar -> array match
            if isinstance(res, (int, float, np.number)):
                return np.full_like(x_values, float(res))
            return np.asarray(res, dtype=float)
        except Exception as e:
            raise UnsafeExpressionError(f"Numerical evaluation failed: {str(e)}") from e
