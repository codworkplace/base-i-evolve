import pytest
from unittest.mock import Mock, patch
from app.real.llm_evaluator import LLMEvaluator


class MockResponse:
    def __init__(self, content):
        # Вложенные объекты для имитации response.choices[0].message.content
        self.choices = [type('', (), {'message': type('', (), {'content': content})()})()]


@pytest.mark.asyncio
async def test_evaluate_case_success():
    mock_response = MockResponse('{"total_score": 85, "feedback": "Хорошая работа!", "results": []}')

    with patch("app.real.llm_evaluator.OpenAI") as MockOpenAI:
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        MockOpenAI.return_value = mock_client

        evaluator = LLMEvaluator()
        result = await evaluator.evaluate_case(
            scenario="Тестовый кейс",
            user_answer="Тестовый ответ",
            checklist=["Критерий 1", "Критерий 2"]
        )

        assert result["total_score"] == 85
        assert result["feedback"] == "Хорошая работа!"


@pytest.mark.asyncio
async def test_evaluate_case_with_json_markers():
    mock_response = MockResponse('```json\n{"total_score": 75, "feedback": "Неплохо", "results": []}\n```')

    with patch("app.real.llm_evaluator.OpenAI") as MockOpenAI:
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        MockOpenAI.return_value = mock_client

        evaluator = LLMEvaluator()
        result = await evaluator.evaluate_case(
            scenario="Тестовый кейс",
            user_answer="Тестовый ответ",
            checklist=["Критерий 1"]
        )

        assert result["total_score"] == 75
        assert result["feedback"] == "Неплохо"


@pytest.mark.asyncio
async def test_evaluate_case_llm_error():
    with patch("app.real.llm_evaluator.OpenAI") as MockOpenAI:
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(side_effect=Exception("API Connection Error"))
        MockOpenAI.return_value = mock_client

        evaluator = LLMEvaluator()
        result = await evaluator.evaluate_case(
            scenario="Тестовый кейс",
            user_answer="Тестовый ответ",
            checklist=["Критерий 1", "Критерий 2", "Критерий 3"]
        )

        assert result["total_score"] == 50
        assert "Ошибка" in result["feedback"]
        assert len(result["results"]) == 3
        assert all(r["verdict"] == "нет" for r in result["results"])


@pytest.mark.asyncio
async def test_evaluate_case_invalid_json():
    mock_response = MockResponse("Извините, я не могу оценить этот ответ")

    with patch("app.real.llm_evaluator.OpenAI") as MockOpenAI:
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        MockOpenAI.return_value = mock_client

        evaluator = LLMEvaluator()
        result = await evaluator.evaluate_case(
            scenario="Тестовый кейс",
            user_answer="Тестовый ответ",
            checklist=["Критерий 1"]
        )

        assert result["total_score"] == 50
        assert "Ошибка" in result["feedback"]


@pytest.mark.asyncio
async def test_generate_feedback():
    mock_response = MockResponse("Конструктивная обратная связь")

    with patch("app.real.llm_evaluator.OpenAI") as MockOpenAI:
        mock_client = Mock()
        mock_client.chat.completions.create = Mock(return_value=mock_response)
        MockOpenAI.return_value = mock_client

        evaluator = LLMEvaluator()
        feedback = await evaluator.generate_feedback(
            user_answer="Тестовый ответ",
            case_scenario="Тестовый кейс",
            evaluation_result={"total_score": 85, "feedback": "Хорошо"}
        )

        assert feedback == "Конструктивная обратная связь"