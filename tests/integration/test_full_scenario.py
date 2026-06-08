from fastapi.testclient import TestClient
from sqlalchemy import text


def test_full_user_journey(client: TestClient, db_session):
    """Тест полного сценария: выбор роли, кейса, отправка ответа и проверка БД"""

    # 1. Получение ролей
    response = client.get("/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) > 0
    print(f"✅ Роли получены: {len(roles)}")

    # 2. Выбор роли и получение компетенций
    role_id = roles[0]["id"]
    response = client.get(f"/roles/{role_id}")
    assert response.status_code == 200
    role_data = response.json()
    competencies = role_data["competencies"]
    assert len(competencies) > 0
    print(f"✅ Компетенции получены: {len(competencies)}")

    # 3. Выбор кейса для первой компетенции
    user_id = "test_user_001"
    first_comp = competencies[0]
    response = client.post(
        "/cases/select",
        json={
            "user_id": user_id,
            "competency_id": first_comp["code"],
            "user_level": 0.5,
            "role_id": role_id,
        },
    )
    assert response.status_code == 200
    case = response.json()
    assert "scenario" in case
    print(f"✅ Кейс выбран: {case.get('title', 'Без названия')}")

    # 4. Отправка ответа на кейс
    test_answer = "Я бы спросил клиента: 'А какие у вас текущие показатели?'"
    response = client.post(
        "/cases/evaluate",
        json={
            "user_id": user_id,
            "competency_id": first_comp["code"],
            "answer": test_answer,
            "role_id": role_id,
        },
    )
    assert response.status_code == 200
    evaluation = response.json()

    # 5. Проверка структуры ответа
    assert "total_score" in evaluation
    assert "passed" in evaluation
    assert "feedback" in evaluation
    assert 0 <= evaluation["total_score"] <= 100
    print(f"✅ Оценка получена: {evaluation['total_score']}%, passed={evaluation['passed']}")

    # 6. Проверка, что пользователь создался в БД
    result = db_session.execute(
        text("SELECT * FROM users WHERE user_id = :user_id"),
        {"user_id": user_id}
    ).first()
    assert result is not None, "Пользователь не найден в БД"
    print(f"✅ Пользователь {user_id} найден в БД, role_id={result.role_id}")

    # 7. Проверка, что результат кейса сохранился
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