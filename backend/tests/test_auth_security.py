import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings

settings.MOCK_MODE = True
client = TestClient(app)

def test_unauthenticated_request_rejected():
    res = client.get("/api/v1/applications")
    assert res.status_code == 401

def test_health_check_public():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"

def test_mock_auth_mode():
    headers = {"Authorization": "Bearer mock-user-candidate-a"}
    # Should authenticate and return empty list or applications
    # Depending on firestore availability in test mode
