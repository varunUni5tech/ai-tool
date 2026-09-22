"""Automatic Pydantic validation and LLM repair loop implementation."""

import json
import logging
from typing import Dict, Any, Tuple
from ai_simulation_engine.schemas.universal_v2 import UniversalSimulationSpec
from ai_simulation_engine.ai.providers.base import AIProvider
from ai_simulation_engine.ai.prompts.system_prompt import get_system_prompt
from ai_simulation_engine.config.settings import settings
from ai_simulation_engine.errors.exceptions import SimulationValidationError

logger = logging.getLogger("ai_simulation_engine.repair_loop")


def clean_json_response(raw_text: str) -> str:
    """Extract raw JSON text from markdown blocks or extra surrounding whitespace."""
    text = raw_text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1]
    if text.endswith("```"):
        text = text.rsplit("```", 1)[0]
    return text.strip()


def validate_and_repair_spec(
    provider: AIProvider,
    prompt: str,
    max_repair_attempts: int = None,
) -> Tuple[UniversalSimulationSpec, int]:
    """Execute LLM generation -> Pydantic validation -> Repair loop up to max_repair_attempts.
    
    Returns:
        Tuple[UniversalSimulationSpec, int]: Validated spec object and total repair count used.
    """
    attempts = max_repair_attempts if max_repair_attempts is not None else settings.simulation_max_repair_attempts
    system_prompt = get_system_prompt()
    current_prompt = f"Generate a valid simulation specification for: {prompt}"
    repair_count = 0

    for attempt in range(attempts + 1):
        try:
            # Generate raw spec dict from provider
            raw_spec = provider.generate_spec(current_prompt)

            # If provider returned a Dict, attempt validation directly
            if isinstance(raw_spec, dict):
                spec_dict = raw_spec
            elif isinstance(raw_spec, str):
                cleaned = clean_json_response(raw_spec)
                spec_dict = json.loads(cleaned)
            else:
                raise ValueError(f"Unexpected spec output type: {type(raw_spec)}")

            # Attempt schema validation (v2.0 or legacy v1.0 migration)
            if "schema_version" in spec_dict and spec_dict["schema_version"] == "2.0":
                spec = UniversalSimulationSpec.model_validate(spec_dict)
            else:
                spec = UniversalSimulationSpec.from_v1_dict(spec_dict)

            logger.info(
                f"[REPAIR LOOP SUCCESS] Prompt validated successfully on attempt {attempt+1} (repairs: {attempt})"
            )
            return spec, attempt

        except Exception as err:
            repair_count = attempt
            logger.warning(
                f"[REPAIR LOOP FAILURE] Validation failed on attempt {attempt+1}/{attempts+1}: {str(err)}"
            )

            if attempt >= attempts:
                raise SimulationValidationError(
                    f"Simulation specification validation failed after {attempts} repair attempts: {str(err)}"
                ) from err

            # Construct repair prompt for next iteration
            current_prompt = (
                f"Your previous JSON specification for prompt '{prompt}' had validation errors:\n"
                f"ERROR DETAILS: {str(err)}\n\n"
                f"Please fix the JSON payload and return ONLY valid JSON matching schema_version '2.0'."
            )
