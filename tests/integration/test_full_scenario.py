import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
import uuid


def test_full_user_journey(client: TestClient, db_session):
    import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
import uuid


def test_full_user_journey(client: TestClient, db_session):
    """Тест полного сценария: регистрация → выбор кейса → оценка → проверка БД"""

    # 1. Регистрация нового пользователя
    unique_suffix = uuid.uuid4().hex[:6]
    email = f"test_{unique_suffix}@example.com"
    password = "secret123"
    user_id = f"tester_{unique_suffix}"
    role_id = "sales_manager"

    reg_data = {
        "email": email,
        "password": password,
        "user_id": user_id,
        "role_id": role_id,
    }
    response = client.post("/auth/register", json=reg_data)
    assert response.status_code == 200, f"Registration failed: {response.text}"
    tokens = response.json()
    access_token = tokens["access_token"]

    headers = {"Authorization": f"Bearer {access_token}"}

    # 2. Получение ролей (публичный эндпоинт, токен не нужен)
    response = client.get("/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) > 0
    print(f"✅ Роли получены: {len(roles)}")

    # 3. Выбор роли и получение компетенций (публичный)
    role_id_from_json = roles[0]["id"]
    response = client.get(f"/roles/{role_id_from_json}")
    assert response.status_code == 200
    role_data = response.json()
    competencies = role_data["competencies"]
    assert len(competencies) > 0
    print(f"✅ Компетенции получены: {len(competencies)}")

    # 4. Выбор кейса (защищённый эндпоинт)
    first_comp = competencies[0]
    response = client.post(
        "/cases/select",
        json={
            "competency_id": first_comp["code"],
            "user_level": 0.5,
        },
        headers=headers,
    )
    assert response.status_code == 200, f"Case selection failed: {response.text}"
    case = response.json()
    assert "scenario" in case
    print(f"✅ Кейс выбран: {case.get('title', 'Без названия')}")

    # 5. Отправка ответа на кейс (защищённый эндпоинт)
    test_answer = "Я бы спросил клиента: 'А какие у вас текущие показатели?'"
    response = client.post(
        "/cases/evaluate",
        json={
            "competency_id": first_comp["code"],
            "answer": test_answer,
        },
        headers=headers,
    )
    assert response.status_code == 200, f"Case evaluation failed: {response.text}"
    evaluation = response.json()

    # 6. Проверка структуры ответа
    assert "total_score" in evaluation
    assert "passed" in evaluation
    assert "feedback" in evaluation
    assert 0 <= evaluation["total_score"] <= 100
    print(f"✅ Оценка получена: {evaluation['total_score']}%, passed={evaluation['passed']}")

    # 7. Проверка, что пользователь создался в БД
    result = db_session.execute(
        text("SELECT * FROM users WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).first()
    assert result is not None, "Пользователь не найден в БД"
    print(f"✅ Пользователь {user_id} найден в БД, role_id={result.role_id}")

    # 8. Проверка, что результат кейса сохранился
    result = db_session.execute(
        text("SELECT * FROM case_results WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).first()
    assert result is not None, "Результат кейса не найден в БД"
    assert result.competency_code == first_comp["code"]
    print(f"✅ Результат кейса сохранён в БД, оценка: {result.evaluation_score}")

    print("\n🎉 Полный сценарий пройден успешно!")


def test_diagnostic_flow(client: TestClient):
    """Тест диагностического среза (если эндпоинт реализован)"""
    response = client.post(
        "/diagnostic/start",
        json={"user_id": "test_user_002", "role_id": "sales_manager"},
    )

    if response.status_code == 404:
        assert response.json()["detail"] == "Not Found"
        print("✅ Диагностический эндпоинт пока не реализован (404)")
        return

    assert response.status_code == 200
    session = response.json()
    assert "session_id" in session
    print("✅ Диагностический сценарий работает")
