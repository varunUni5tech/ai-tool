"""OpenAI AI Provider implementation."""

import json
from typing import Dict, Any
from ai_simulation_engine.ai.providers.base import AIProvider
from ai_simulation_engine.config.settings import settings
from ai_simulation_engine.errors.exceptions import AIParsingError


SYSTEM_PROMPT = """You are an AI Simulation Spec Generator.
Convert natural language prompt into a valid JSON simulation spec adhering to the schema.
Only return pure JSON.
Allowed simulation types:
- function_plot (domain: mathematics)
- projectile_motion (domain: mechanics)
- optical_prism (domain: optics)
- prism_dispersion (domain: optics)
"""


class OpenAIProvider(AIProvider):
    """OpenAI JSON specification generator provider."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.openai_api_key

    def generate_spec(self, prompt: str) -> Dict[str, Any]:
        if not self.api_key:
            raise AIParsingError("OpenAI API key is missing. Configure OPENAI_API_KEY in environment.")

        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.0,
            )
            raw_json = response.choices[0].message.content
            return json.loads(raw_json)
        except Exception as e:
            raise AIParsingError(f"OpenAI spec generation failed: {str(e)}") from e
