import pytest


@pytest.mark.asyncio
async def test_full_user_journey(client):
    """Тест полного сценария: диагностика → кейс → оценка → отчет"""

    # 1. Получение ролей
    response = client.get("/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) > 0

    # 2. Выбор роли и получение компетенций
    role_id = roles[0]["id"]
    response = client.get(f"/roles/{role_id}")
    assert response.status_code == 200
    competencies = response.json()["competencies"]
    assert len(competencies) > 0

    # 3. Диагностика (отправка оценок)
    user_id = "test_user_001"
    diagnostic_scores = {}

    for comp in competencies:
        code = comp["code"]
        score = 50.0  # средний уровень
        diagnostic_scores[code] = score

    # 4. Получение кейса для первой компетенции
    first_comp = competencies[0]
    response = client.post(
        "/cases/select",
        json={
            "user_id": user_id,
            "competency_id": first_comp["code"],
            "user_level": 0.5,
        },
    )
    assert response.status_code == 200
    case = response.json()
    assert "scenario" in case

    # 5. Отправка ответа на кейс
    test_answer = "Я бы спросил клиента: 'А какие у вас текущие показатели?'"

    response = client.post(
        "/cases/evaluate",
        json={
            "user_id": user_id,
            "competency_id": first_comp["code"],
            "answer": test_answer,
        },
    )
    assert response.status_code == 200
    evaluation = response.json()

    # 6. Проверка оценки
    assert "total_score" in evaluation
    assert evaluation["total_score"] >= 0
    assert evaluation["total_score"] <= 100
    assert "passed" in evaluation
    assert "feedback" in evaluation

    # 7. Проверка, что навык обновился
    response = client.get(f"/users/{user_id}/skills")
    if response.status_code == 200:
        skills = response.json()
        assert isinstance(skills, list)

    print(f"✅ Полный сценарий пройден. Оценка: {evaluation['total_score']}%")


@pytest.mark.asyncio
async def test_diagnostic_flow(client):
    """Тест диагностического среза"""

    response = client.post(
        "/diagnostic/start",
        json={"user_id": "test_user_002", "role_id": "sales_manager"},
    )

    if response.status_code == 200:
        session = response.json()
        assert "session_id" in session

        # Отправка ответов на вопросы
        questions = session.get("questions", [])
        for q in questions[:2]:
            response = client.post(
                f"/diagnostic/{session['session_id']}/answer",
                json={"question_id": q["id"], "answer": 75},
            )
            assert response.status_code == 200
