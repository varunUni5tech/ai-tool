"""OpenAI AI Provider implementation."""

import json
from typing import Dict, Any
from ai_simulation_engine.ai.providers.base import AIProvider
from ai_simulation_engine.config.settings import settings
from ai_simulation_engine.errors.exceptions import AIParsingError


SYSTEM_PROMPT = """You are an Autonomous AI 3D Physics Engine and Mathematical Evaluator.
Your goal is to parse ANY natural language physics or mathematics simulation prompt and return a complete, accurate 3D numerical dataset JSON payload ready for Three.js 3D rendering.

You must handle ANY requested topic (e.g., Optics Refraction, Rainbow Prism Dispersion, Projectile Motion, Gravitational Orbits, Pendulums, Wave Interference, Calculus Function Curves).

Return ONLY valid JSON with this exact schema:
{
  "simulation_type": "string (e.g. prism_dispersion, projectile_motion, pendulum, orbit, function_plot)",
  "domain": "string (e.g. optics, mechanics, astrophysics, mathematics)",
  "parameters": {
    "key_param_1": "float/string"
  },
  "summary": {
    "key_metric_name": "float or string description",
    "math_formula_used": "string"
  },
  "trajectoryPoints": [
    [x0, y0, z0],
    [x1, y1, z1],
    ...
  ],
  "rays": [
    {
      "wavelengthNm": 700,
      "refractiveIndex": 1.508,
      "color": "#FF0000",
      "spectralName": "Red 700nm",
      "deviationAngleDeg": 49.2,
      "isTotalInternalReflection": false,
      "incident": {"origin": [-3.5, 0, 0], "intersection": [-1.0, 0, 0]},
      "inside": {"origin": [-1.0, 0, 0], "intersection": [1.0, 0, 0]},
      "outgoing": {"endPoint": [3.5, -1.5, 0]}
    }
  ],
  "educational": {
    "subject": "Physics or Mathematics",
    "chapter": "Chapter Name",
    "topic": "Topic Name",
    "difficulty": "Class 11 or Class 12"
  }
}
"""


class OpenAIProvider(AIProvider):
    """OpenAI Autonomous Physics Engine Provider."""

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
                    {"role": "user", "content": f"Generate complete 3D simulation data for: {prompt}"},
                ],
                temperature=0.1,
            )
            raw_json = response.choices[0].message.content
            return json.loads(raw_json)
        except Exception as e:
            raise AIParsingError(f"OpenAI spec generation failed: {str(e)}") from e
