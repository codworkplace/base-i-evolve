# tests/test_roles.py
from fastapi.testclient import TestClient


def test_roles_endpoint(client: TestClient):
    response = client.get("/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) > 0
    print(f"✅ Найдено ролей: {len(roles)}")


def test_root_endpoint(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"
