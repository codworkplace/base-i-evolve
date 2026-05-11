# test_evaluate.py
import asyncio
from app.real.llm_evaluator import LLMEvaluator

async def test_evaluation():
    evaluator = LLMEvaluator()
    
    scenario = "Вы звоните клиенту. Он говорит: 'Мне ничего не нужно, у нас все хорошо.'"
    answer = "Здравствуйте! А какие цели на следующий квартал вы ставите? Может быть, есть планы по росту?"
    checklist = [
        "Задал открытый вопрос о планах",
        "Не согласился сразу с отказом",
        "Проявил интерес к бизнесу клиента"
    ]
    
    print("Оцениваю ответ...")
    result = await evaluator.evaluate_case(scenario, answer, checklist)
    
    print("\nРезультат оценки:")
    print(f"Общий балл: {result.get('total_score')}%")
    print(f"Feedback: {result.get('feedback')}")
    print("\nДетали:")
    for r in result.get('results', []):
        print(f"  {r['criterion']}: {r['verdict']}")
        print(f"    Evidence: {r.get('evidence', '')}")

if __name__ == "__main__":
    asyncio.run(test_evaluation())