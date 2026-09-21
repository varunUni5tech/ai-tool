"""Integration tests for FastAPI endpoints using TestClient."""

import pytest
from fastapi.testclient import TestClient
from ai_simulation_engine.api.app import app

client = TestClient(app)


def test_health_check_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert len(data["registered_simulations"]) >= 4


def test_generate_spec_endpoint():
    payload = {"prompt": "Show projectile motion, 20 m/s at 45 deg", "provider": "mock"}
    response = client.post("/simulations/generate", json=payload)
    assert response.status_code == 200
    spec = response.json()
    assert spec["simulation_type"] == "projectile_motion"
    assert spec["domain"] == "mechanics"


def test_run_simulation_endpoint():
    payload = {
        "simulation_schema_version": "1.0",
        "simulation_type": "function_plot",
        "domain": "mathematics",
        "parameters": {"expression": "sin(x)"}
    }
    response = client.post("/simulations/run", json=payload)
    assert response.status_code == 200
    result = response.json()
    assert result["simulation_type"] == "function_plot"
    assert "data" in result
    assert "x" in result["data"]
    assert "y" in result["data"]


def test_math_graph_express():
    payload = {"expression": "exp(-x)*cos(x)"}
    response = client.post("/math/graph", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["summary"]["expression"] == "exp(-x)*cos(x)"


def test_physics_simulate_express():
    payload = {"initial_velocity": 25.0, "launch_angle": 30.0}
    response = client.post("/physics/simulate", json=payload)
    assert response.status_code == 200
    res = response.json()
    assert res["summary"]["initial_velocity"] == 25.0


def test_html_visualization_endpoints():
    payload = {"prompt": "Show projectile motion, 20 m/s at 45 deg", "provider": "mock"}
    response = client.post("/api/v1/simulations/generate-and-run/html", json=payload)
    assert response.status_code == 200
    assert "<html" in response.text.lower()
    assert "plotly" in response.text.lower()


def test_html3d_visualization_endpoints():
    payload = {"prompt": "Show dispersion of white light through a prism", "provider": "mock"}
    response = client.post("/api/v1/simulations/generate-and-run/html3d", json=payload)
    assert response.status_code == 200
    assert "<html" in response.text.lower()
    assert "plotly" in response.text.lower()
