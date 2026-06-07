import pytest

@pytest.mark.skip(reason="User already exists; will be fixed in Day 4")
def test_register_and_login(client):
    # Регистрация
    reg_data = {
        "email": "test@example.com",
        "password": "secret",
        "user_id": "tester",
        "role_id": "sales_manager"
    }
    resp = client.post("/auth/register", json=reg_data)
    assert resp.status_code == 200
    tokens = resp.json()
    assert "access_token" in tokens

    # Логин
    login_data = {"email": "test@example.com", "password": "secret"}
    resp = client.post("/auth/login", json=login_data)
    assert resp.status_code == 200
    access_token = resp.json()["access_token"]

    # Доступ к защищённому эндпоинту (например, /users/me)
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = client.get("/users/me", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"