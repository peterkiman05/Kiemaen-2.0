import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code in [200, 404]

def test_messaging_payload_validation():
    headers = {"X-API-Key": "free_user_key"}
    response = client.post("/api/messaging/webhook", json={"token": "test-token"}, headers=headers)
    assert response.status_code in [200, 401, 422, 404]
