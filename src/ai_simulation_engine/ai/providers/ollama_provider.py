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

    def __init__(self, host_url: str = None, model_name: str = None):
        self.host_url = (host_url or settings.ollama_host).rstrip("/")
        self.model_name = model_name or settings.ollama_model

    def _get_available_model(self) -> str:
        """Fetch installed models from Ollama and pick first if specified model is missing."""
        try:
            req = urllib.request.Request(f"{self.host_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m.get("name") for m in data.get("models", []) if m.get("name")]
                if models:
                    if self.model_name in models:
                        return self.model_name
                    # If specified model not found, return first available model
                    return models[0]
        except Exception:
            pass
        return self.model_name

    def generate_spec(self, prompt: str) -> Dict[str, Any]:
        target_model = self._get_available_model()
        url = f"{self.host_url}/api/generate"
        payload = {
            "model": target_model,
            "system": SYSTEM_PROMPT,
            "prompt": f"Generate complete 3D simulation data for: {prompt}",
            "format": "json",
            "stream": False,
        }
        try:
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})

            with urllib.request.urlopen(req, timeout=120) as response:
                res_body = response.read().decode("utf-8")
                res_json = json.loads(res_body)
                raw_text = res_json.get("response", "").strip()

                # Clean markdown codeblocks if model wraps output in ```json ... ```
                if raw_text.startswith("```"):
                    raw_text = raw_text.split("\n", 1)[-1]
                if raw_text.endswith("```"):
                    raw_text = raw_text.rsplit("```", 1)[0]
                raw_text = raw_text.strip()

                return json.loads(raw_text)
        except Exception as e:
            raise AIParsingError(f"Ollama local AI spec generation failed (model='{target_model}'): {str(e)}") from e

