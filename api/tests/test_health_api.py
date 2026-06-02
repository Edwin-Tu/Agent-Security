from fastapi.testclient import TestClient
from api.server import app

client = TestClient(app)


def test_health_api_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "secretguard"
    assert "version" in data
