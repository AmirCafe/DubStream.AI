import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_register_endpoint(client):
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "securepass123",
        "full_name": "Test User"
    })
    assert response.status_code in [200, 201, 409]  # Created or conflict

def test_rate_limiting(client):
    for i in range(150):
        response = client.get("/health")
        if response.status_code == 429:
            assert True
            return
    assert False, "Rate limiting not working"
