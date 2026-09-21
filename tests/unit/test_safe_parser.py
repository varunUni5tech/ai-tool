"""Unit tests for the safe SymPy expression parser."""

import pytest
from ai_simulation_engine.math_engine.expression.parser import SafeExpressionParser
from ai_simulation_engine.math_engine.expression.evaluator import SafeExpressionEvaluator
from ai_simulation_engine.errors.exceptions import UnsafeExpressionError
import numpy as np


def test_valid_expression_parsing():
    parser = SafeExpressionParser(allowed_variables={"x"})
    expr = parser.parse("sin(x) + cos(x) * exp(-x)")
    assert expr is not None


def test_unsafe_expression_rejection_eval():
    parser = SafeExpressionParser(allowed_variables={"x"})
    with pytest.raises(UnsafeExpressionError):
        parser.parse("eval('1+1')")


def test_unsafe_expression_rejection_import():
    parser = SafeExpressionParser(allowed_variables={"x"})
    with pytest.raises(UnsafeExpressionError):
        parser.parse("__import__('os').system('ls')")


def test_disallowed_function():
    parser = SafeExpressionParser(allowed_variables={"x"})
    with pytest.raises(UnsafeExpressionError):
        parser.parse("custom_function(x)")


def test_vectorized_evaluator():
    evaluator = SafeExpressionEvaluator("sin(x)", var_name="x")
    x = np.array([0.0, np.pi / 2, np.pi])
    y = evaluator.evaluate_grid(x)
    np.testing.assert_allclose(y, [0.0, 1.0, 0.0], atol=1e-5)
