"""Dynamic rule & regex AI Provider for NL -> JSON Spec generation."""

import re
from typing import Dict, Any
from ai_simulation_engine.ai.providers.base import AIProvider


class MockAIProvider(AIProvider):
    """Dynamic pattern & regex matching provider parsing angles, velocities, and expressions from natural language."""

    def generate_spec(self, prompt: str) -> Dict[str, Any]:
        p = prompt.lower().strip()

        # Default values
        apex_angle = 60.0
        incident_angle = 30.0

        # Extract apex angle (e.g. "apex angle 50", "apex 50", "50 deg apex")
        apex_match = re.search(r"apex(?:\s+angle)?(?:\s+of)?\s*(\d+(?:\.\d+)?)", p)
        if not apex_match:
            apex_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:deg|°|degree)?\s*apex", p)
        if apex_match:
            try:
                apex_angle = float(apex_match.group(1))
            except Exception:
                apex_angle = 60.0

        # Extract incident angle (e.g. "incident angle 40", "incident 40", "40 deg incident", "at 40 deg")
        inc_match = re.search(r"incident(?:\s+angle)?(?:\s+of)?\s*(\d+(?:\.\d+)?)", p)
        if not inc_match:
            inc_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:deg|°|degree)?\s*incident", p)
        if not inc_match:
            inc_match = re.search(r"at\s+(\d+(?:\.\d+)?)\s*(?:deg|°|degree)", p)
        if inc_match:
            try:
                val = float(inc_match.group(1))
                if val < 90:
                    incident_angle = val
            except Exception:
                incident_angle = 30.0

        # 1. Projectile Motion match (e.g. "projectile motion 20 m/s at 45 deg")
        if "projectile" in p or "launch" in p or "trajectory" in p:
            v0 = 20.0
            angle = 45.0
            v_match = re.search(r"(\d+(\.\d+)?)\s*m/s", p)
            if v_match:
                v0 = float(v_match.group(1))

            a_match = re.search(r"(\d+(\.\d+)?)\s*(deg|°|degree|at)", p)
            if a_match:
                angle = float(a_match.group(1))

            return {
                "simulation_schema_version": "1.0",
                "simulation_type": "projectile_motion",
                "domain": "mechanics",
                "parameters": {
                    "initial_velocity": v0,
                    "launch_angle": angle,
                    "initial_height": 0.0,
                    "gravity": 9.81,
                    "time_step": 0.05,
                },
                "visualization": {"type": "trajectory_2d", "animated": True, "title": "Projectile Motion Trajectory"},
                "educational": {
                    "subject": "Physics",
                    "chapter": "Kinematics",
                    "topic": "2D Motion under Gravity",
                    "difficulty": "Class 11",
                },
            }

        # 2. Math Function Plotting match (e.g. "plot sin(x)", "sin(x)/cos(x)", "graph cos(x)")
        if "plot" in p or "graph" in p or "function" in p or "sin" in p or "cos" in p or "tan" in p or ("/" in p and "m/s" not in p):
            expr = "sin(x)"
            if "sin(x)/cos(x)" in p or "sin/cos" in p or "tan" in p:
                expr = "sin(x)/cos(x)"
            elif "cos" in p and "sin" not in p:
                expr = "cos(x)"
            elif "exp" in p:
                expr = "exp(-x)*cos(2*x)"
            
            # Check for explicit expression match
            expr_match = re.search(r"(?:plot|graph|expression|of)\s+([a-zA-Z0-9\(\)\/\*\+\-\s]+)", p)
            if expr_match:
                extracted = expr_match.group(1).strip()
                if any(k in extracted for k in ["sin", "cos", "tan", "x", "/"]):
                    expr = extracted.replace(" ", "")

            return {
                "simulation_schema_version": "1.0",
                "simulation_type": "function_plot",
                "domain": "mathematics",
                "parameters": {
                    "expression": expr,
                    "domain": {"min": 0.0, "max": 6.283185307179586, "samples": 200},
                },
                "visualization": {"type": "function_plot", "title": f"Plot of {expr}"},
                "educational": {
                    "subject": "Mathematics",
                    "chapter": "Calculus & Trigonometry",
                    "topic": "Function Analysis",
                    "difficulty": "Class 11",
                },
            }

        # Default: Prism Spectral Dispersion (Optics) with dynamic apex & incident angles parsed from prompt
        return {
            "simulation_schema_version": "1.0",
            "simulation_type": "prism_dispersion",
            "domain": "optics",
            "parameters": {
                "apex_angle": apex_angle,
                "incident_angle": incident_angle,
                "cauchy_b": 1.50,
                "cauchy_c": 0.004,
                "wavelengths_nm": [700.0, 620.0, 580.0, 530.0, 470.0, 420.0],
            },
            "visualization": {"type": "dispersion_spectrum", "title": "Prism Spectral Dispersion"},
            "educational": {
                "subject": "Physics",
                "chapter": "Ray Optics",
                "topic": "Dispersion of Light",
                "difficulty": "Class 12",
            },
        }
