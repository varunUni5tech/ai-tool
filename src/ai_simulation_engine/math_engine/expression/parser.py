"""Safe SymPy expression parser and AST validator."""

import sympy as sp
from typing import Set, Dict, Any
from ai_simulation_engine.errors.exceptions import UnsafeExpressionError

# Strict whitelist of allowed functions and constants
ALLOWED_FUNCTIONS = {
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "sqrt": sp.sqrt,
    "log": sp.log,
    "ln": sp.log,
    "exp": sp.exp,
    "abs": sp.Abs,
}

ALLOWED_CONSTANTS = {
    "pi": sp.pi,
    "e": sp.E,
    "E": sp.E,
}


class SafeExpressionParser:
    """Parses mathematical strings safely using SymPy AST validation."""

    def __init__(self, allowed_variables: Set[str] = None):
        self.allowed_variables = allowed_variables or {"x", "t", "y"}

    def parse(self, expr_str: str) -> sp.Expr:
        """Parse string expression into SymPy expression safely."""
        if not expr_str or not isinstance(expr_str, str):
            raise UnsafeExpressionError("Expression must be a non-empty string.")

        # Guard length
        if len(expr_str) > 200:
            raise UnsafeExpressionError("Expression exceeds maximum allowed length (200 chars).")

        # Disallow suspicious keywords as whole words or double underscore
        import re
        if "__" in expr_str:
            raise UnsafeExpressionError("Forbidden double underscore '__' detected in expression.")

        forbidden_pattern = r"\b(import|exec|eval|lambda|os|sys|subprocess|open|read)\b"
        if re.search(forbidden_pattern, expr_str.lower()):
            raise UnsafeExpressionError("Forbidden keyword detected in expression.")

        try:
            # Parse with sympy sympify using restricted local dictionary
            local_dict: Dict[str, Any] = {}
            for var in self.allowed_variables:
                local_dict[var] = sp.Symbol(var)
            local_dict.update(ALLOWED_FUNCTIONS)
            local_dict.update(ALLOWED_CONSTANTS)

            expr = sp.sympify(expr_str, locals=local_dict, evaluate=False)
            self._validate_ast(expr)
            return expr
        except Exception as e:
            if isinstance(e, UnsafeExpressionError):
                raise
            raise UnsafeExpressionError(f"Failed to safely parse expression '{expr_str}': {str(e)}") from e

    def _validate_ast(self, node: sp.Basic) -> None:
        """Recursively validate SymPy AST node types."""
        # Limit AST depth / size
        if len(node.atoms()) > 50:
            raise UnsafeExpressionError("Expression AST complexity exceeds safety limit.")

        for subexpr in sp.preorder_traversal(node):
            if isinstance(subexpr, sp.Symbol):
                if subexpr.name not in self.allowed_variables and subexpr.name not in ALLOWED_CONSTANTS:
                    raise UnsafeExpressionError(f"Disallowed variable symbol: {subexpr.name}")
            elif isinstance(subexpr, sp.Function):
                func_name = subexpr.func.__name__
                if func_name not in ALLOWED_FUNCTIONS:
                    raise UnsafeExpressionError(f"Disallowed mathematical function: {func_name}")
