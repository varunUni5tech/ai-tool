"""Integration tests for universal POST /simulate endpoint."""

import pytest
from fastapi.testclient import TestClient
from ai_simulation_engine.api.app import app

client = TestClient(app)


def test_simulate_endpoint_mock_provider():
    payload = {"prompt": "Show projectile motion 20 m/s at 45 deg", "provider": "mock"}
    response = client.post("/simulate", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert "request_id" in body
    assert "simulation_spec" in body
    assert "result" in body
    assert "visualization" in body

    spec = body["simulation_spec"]
    assert spec["schema_version"] == "2.0"
    assert spec["simulation"]["type"] == "projectile_motion"
