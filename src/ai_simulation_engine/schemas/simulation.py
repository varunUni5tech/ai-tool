"""Schema validation utilities."""

import json
from pathlib import Path
from typing import Dict, Any
from ai_simulation_engine.models.simulation import SimulationSpec
from ai_simulation_engine.errors.exceptions import SimulationValidationError


def validate_spec_dict(data: Dict[str, Any]) -> SimulationSpec:
    """Validate a raw spec dict using Pydantic SimulationSpec."""
    try:
        return SimulationSpec.model_validate(data)
    except Exception as e:
        raise SimulationValidationError(f"Spec validation failed: {str(e)}") from e


def load_json_schema(name: str) -> Dict[str, Any]:
    """Load JSON Schema from schemas/json directory."""
    schema_path = Path(__file__).parents[2] / "schemas" / "json" / f"{name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"JSON schema not found: {schema_path}")
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)
