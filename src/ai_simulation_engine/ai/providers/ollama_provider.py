"""Ollama AI Provider implementation for local offline LLM generation."""

import json
import urllib.request
from typing import Dict, Any
from ai_simulation_engine.ai.providers.base import AIProvider
from ai_simulation_engine.config.settings import settings
from ai_simulation_engine.errors.exceptions import AIParsingError


SYSTEM_PROMPT = """You are an Autonomous AI 3D Physics Engine and Mathematical Evaluator.
Your goal is to parse ANY natural language physics or mathematics simulation prompt and return a complete, accurate 3D numerical dataset JSON payload ready for Three.js 3D rendering.

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
    [x1, y1, z1]
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


class OllamaProvider(AIProvider):
    """Ollama local AI specification & 3D dataset generator provider."""

    def __init__(self, host_url: str = "http://localhost:11434", model_name: str = "llama3.1"):
        self.host_url = host_url
        self.model_name = model_name

    def generate_spec(self, prompt: str) -> Dict[str, Any]:
        try:
            url = f"{self.host_url}/api/generate"
            payload = {
                "model": self.model_name,
                "system": SYSTEM_PROMPT,
                "prompt": f"Generate complete 3D simulation data for: {prompt}",
                "format": "json",
                "stream": False,
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

            with urllib.request.urlopen(req, timeout=60) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                raw_response_text = res_json.get("response", "")
                return json.loads(raw_response_text)
        except Exception as e:
            raise AIParsingError(f"Ollama local AI spec generation failed: {str(e)}") from e
