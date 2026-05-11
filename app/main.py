# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from pathlib import Path
from app.real.llm_evaluator import LLMEvaluator
from app.real.case_selector import CaseSelector

app = FastAPI(title="BS-Evolve API")

# Инициализация сервисов
llm_evaluator = LLMEvaluator()
case_selector = CaseSelector()

# Хранилище для кейсов пользователей (временно in-memory)
user_sessions = {}

# Разрешаем запросы из Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ПРИНУДИТЕЛЬНО устанавливаем UTF-8 для всех ответов
@app.middleware("http")
async def set_charset_header(request, call_next):
    response = await call_next(request)
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

DATA_DIR = Path("data")
ROLES_FILE = DATA_DIR / "roles.json"
COMPETENCIES_FILE = DATA_DIR / "competencies.json"

def load_roles():
    if ROLES_FILE.exists():
        with open(ROLES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def load_competencies():
    if COMPETENCIES_FILE.exists():
        with open(COMPETENCIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

@app.get("/")
async def root():
    return JSONResponse(
        content={"message": "BS-Evolve API", "status": "running"},
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/roles")
async def list_roles():
    roles = load_roles()
    result = [{"id": k, "name": v.get("name", k)} for k, v in roles.items()]
    # Возвращаем с явным указанием кодировки
    return JSONResponse(
        content=result,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

@app.get("/roles/{role_id}")
async def get_role(role_id: str):
    roles = load_roles()
    competencies = load_competencies()
    
    if role_id not in roles:
        return JSONResponse(
            content={"error": "Role not found"},
            status_code=404,
            headers={"Content-Type": "application/json; charset=utf-8"}
        )
    
    role = roles[role_id]
    role_competencies = []
    for comp_id in role.get("competencies", []):
        if comp_id in competencies:
            role_competencies.append({
                "code": comp_id,
                "name": competencies[comp_id].get("name", comp_id),
                "type": competencies[comp_id].get("type", "SOFT"),
                "category": competencies[comp_id].get("category", "SKILL"),
                "description": competencies[comp_id].get("description", "")
            })
    
    result = {
        "id": role_id,
        "name": role.get("name", ""),
        "description": role.get("description", ""),
        "competencies": role_competencies
    }
    
    return JSONResponse(
        content=result,
        headers={"Content-Type": "application/json; charset=utf-8"}
    )

# Добавление новых эндпоинтов:
@app.get("/cases/{competency_id}")
async def get_cases_by_competency(competency_id: str):
    """Получить кейсы по компетенции"""
    with open("data/cases.json", 'r', encoding='utf-8') as f:
        cases = json.load(f)
    
    if competency_id in cases:
        return cases[competency_id]
    return []

@app.post("/cases/select")
async def select_case_for_user(request: dict):
    """Выбрать кейс для пользователя"""
    user_id = request.get("user_id", "test_user")
    competency_id = request.get("competency_id")
    user_level = request.get("user_level", 0.5)
    
    if not competency_id:
        return {"error": "competency_id required"}
    
    case = await case_selector.select_case(competency_id, user_level)
    
    if not case:
        return {"error": "No case available"}
    
    # Сохраняем сессию
    session_key = f"{user_id}_{competency_id}"
    user_sessions[session_key] = {
        "case_id": case.get("id"),
        "scenario": case.get("scenario"),
        "checklist": case.get("checklist", []),
        "competency_id": competency_id
    }
    
    return {
        "case_id": case.get("id"),
        "scenario": case.get("scenario"),
        "checklist": case.get("checklist", []),
        "title": case.get("title", "")
    }

@app.post("/cases/evaluate")
async def evaluate_case(request: dict):
    """Оценить ответ пользователя"""
    user_id = request.get("user_id", "test_user")
    competency_id = request.get("competency_id")
    answer = request.get("answer", "")
    
    session_key = f"{user_id}_{competency_id}"
    
    if session_key not in user_sessions:
        return {"error": "No active case session"}
    
    session = user_sessions[session_key]
    
    # Оцениваем через LLM
    evaluation = await llm_evaluator.evaluate_case(
        scenario=session["scenario"],
        user_answer=answer,
        checklist=session["checklist"]
    )
    
    # Добавляем информацию о кейсе
    evaluation["case_id"] = session["case_id"]
    evaluation["competency_id"] = competency_id
    evaluation["passed"] = evaluation.get("total_score", 0) >= 70
    
    # Очищаем сессию
    del user_sessions[session_key]
    
    return evaluation

@app.get("/health/llm")
async def check_llm_health():
    """Проверка подключения к LLM"""
    try:
        from app.real.llm_evaluator import LLMEvaluator
        evaluator = LLMEvaluator()
        
        # Простой тестовый запрос
        test_result = await evaluator.evaluate_case(
            scenario="Тестовый кейс",
            user_answer="Тестовый ответ",
            checklist=["Тестовый пункт"]
        )
        
        return {
            "status": "healthy",
            "model": evaluator.model,
            "base_url": evaluator.client.base_url,
            "test_score": test_result.get("total_score", 0)
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)