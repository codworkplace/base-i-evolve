import os
import json
from openai import OpenAI
from dotenv import load_dotenv
import structlog

load_dotenv()

logger = structlog.get_logger()


class LLMEvaluator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.vsegpt.ru/v1")

        if not api_key:
            logger.warning("OPENAI_API_KEY not found in .env file")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

        logger.info("llm_evaluator_initialized", model=self.model, base_url=base_url)

    async def evaluate_case(self, scenario: str, user_answer: str, checklist: list):
        logger.info(
            "evaluating_case",
            scenario_preview=scenario[:100],
            answer_length=len(user_answer),
            checklist_items=len(checklist),
        )

        checklist_text = "\n".join(f"- {item}" for item in checklist)

        prompt = f"""
Ты — эксперт по оценке компетенций. Оцени ответ сотрудника.

КЕЙС:
{scenario}

ЧЕК-ЛИСТ (оцени каждый пункт как ДА или НЕТ):
{checklist_text}

ОТВЕТ СОТРУДНИКА:
{user_answer}

Верни ТОЛЬКО JSON в формате:
{{
    "results": [
        {{"criterion": "пункт чек-листа", "verdict": "да/нет", "evidence": "цитата из ответа"}}
    ],
    "total_score": 0-100,
    "feedback": "краткий комментарий на русском"
}}
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
            )

            content = response.choices[0].message.content
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            result = json.loads(content.strip())

            logger.info(
                "evaluation_completed",
                total_score=result.get("total_score"),
                passed=result.get("total_score", 0) >= 70,
            )

            return result

        except Exception as e:
            logger.error(
                "evaluation_failed",
                error=str(e),
                error_type=type(e).__name__,
                scenario_preview=scenario[:100],
                checklist_items=len(checklist),
            )

            results = []
            for criterion in checklist:
                results.append(
                    {
                        "criterion": criterion,
                        "verdict": "нет",
                        "evidence": f"Ошибка API: {str(e)}",
                    }
                )

            return {
                "results": results,
                "total_score": 50,
                "feedback": f"Ошибка при оценке: {str(e)}. Пожалуйста, проверьте API ключ.",
            }

    async def generate_feedback(
        self, user_answer: str, case_scenario: str, evaluation_result: dict
    ):
        logger.info(
            "generating_feedback",
            answer_length=len(user_answer),
            scenario_length=len(case_scenario),
            total_score=evaluation_result.get("total_score"),
        )

        prompt = f"""
На основе оценки ответа сотрудника, напиши конструктивную обратную связь.

Кейс: {case_scenario}
Ответ сотрудника: {user_answer}
Результат оценки: {json.dumps(evaluation_result, ensure_ascii=False)}

Напиши обратную связь (3-5 предложений) на русском языке:
1. Что сделано хорошо
2. Что можно улучшить
3. Конкретный совет
"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
            )

            feedback = response.choices[0].message.content

            logger.info("feedback_generated", feedback_length=len(feedback))

            return feedback

        except Exception as e:
            logger.error(
                "feedback_generation_failed", error=str(e), error_type=type(e).__name__
            )
            return f"Рекомендуется еще раз изучить критерии оценки по данному кейсу. Ошибка: {str(e)}"
