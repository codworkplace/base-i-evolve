import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMEvaluator:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.vsegpt.ru/v1")

        if not api_key:
            print("WARNING: OPENAI_API_KEY not found in .env file")

        self.client = OpenAI(api_key=api_key, base_url=base_url)
        self.model = os.getenv("OPENAI_MODEL", "openai/gpt-4o-mini")

    async def evaluate_case(self, scenario: str, user_answer: str, checklist: list):
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
            return result
        except Exception as e:
            print(f"LLM Error: {e}")
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

            return response.choices[0].message.content
        except Exception as e:
            return f"Рекомендуется еще раз изучить критерии оценки по данному кейсу. Ошибка: {str(e)}"
