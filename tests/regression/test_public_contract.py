"""Regression guard for the initial public health endpoint contract."""

import pytest
from fastapi.testclient import TestClient

from phoenix_ai.api.main import app


@pytest.mark.regression
def test_health_endpoint_contract() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "phoenix-ai-x"}

