from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_roles_endpoint():
    response = client.get("/roles")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_llm_health():
    response = client.get("/health/llm")
    assert response.status_code == 200
    assert response.json()["status"] in ["healthy", "unhealthy"]
