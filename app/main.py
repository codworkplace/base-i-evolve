from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
import json
from pathlib import Path
import os

from app.real.case_selector import CaseSelector
from app.db.base import get_db
from app.services.user_service import UserService
from app.core.logging import setup_logging
from app.routers import auth
from app.dependencies.auth import get_current_user
from app.db.models.user import User
from app.routers import users
from app.routers import admin

# Настройка логирования
environment = os.getenv("ENVIRONMENT", "development")
setup_logging(environment)

app = FastAPI(
    title="BS-Evolve API",
    docs_url=None,
    redoc_url=None,
    openapi_url="/openapi.json",
)

# Подключаем роутер аутентификации (регистрация, логин)
app.include_router(auth.router)

# Подключаем роутер пользователей
app.include_router(users.router)

# Подключаем роутер админа
app.include_router(admin.router)

# Ленивая инициализация LLM
llm_evaluator = None

def get_llm_evaluator():
    global llm_evaluator
    if llm_evaluator is None:
        from app.real.llm_evaluator import LLMEvaluator
        llm_evaluator = LLMEvaluator()
    return llm_evaluator

case_selector = CaseSelector()
user_sessions = {}  # временное in-memory хранилище сессий

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Загрузка данных из JSON
DATA_DIR = Path("data")
ROLES_FILE = DATA_DIR / "roles.json"
COMPETENCIES_FILE = DATA_DIR / "competencies.json"

def load_roles():
    if ROLES_FILE.exists():
        with open(ROLES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_competencies():
    if COMPETENCIES_FILE.exists():
        with open(COMPETENCIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

# ---------- Публичные эндпоинты (не требуют авторизации) ----------
@app.get("/")
async def root():
    return JSONResponse(content={"message": "BS-Evolve API", "status": "running"})

@app.get("/roles")
async def list_roles():
    roles = load_roles()
    result = [{"id": k, "name": v.get("name", k)} for k, v in roles.items()]
    return JSONResponse(content=result)

@app.get("/roles/{role_id}")
async def get_role(role_id: str):
    roles = load_roles()
    competencies = load_competencies()
    if role_id not in roles:
        return JSONResponse(content={"error": "Role not found"}, status_code=404)
    role = roles[role_id]
    role_competencies = []
    for comp_id in role.get("competencies", []):
        if comp_id in competencies:
            role_competencies.append({
                "code": comp_id,
                "name": competencies[comp_id].get("name", comp_id),
                "type": competencies[comp_id].get("type", "SOFT"),
                "category": competencies[comp_id].get("category", "SKILL"),
                "description": competencies[comp_id].get("description", ""),
            })
    return JSONResponse(content={
        "id": role_id,
        "name": role.get("name", ""),
        "description": role.get("description", ""),
        "competencies": role_competencies,
    })

@app.get("/cases/{competency_id}")
async def get_cases_by_competency(competency_id: str):
    with open("data/cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)
    return cases.get(competency_id, [])

@app.get("/health/llm")
async def check_llm_health():
    try:
        evaluator = get_llm_evaluator()
        if not hasattr(evaluator, "client") or evaluator.client is None:
            return {"status": "unhealthy", "error": "LLM not initialized (no API key?)"}
        test_result = await evaluator.evaluate_case(
            scenario="Тестовый кейс",
            user_answer="Тестовый ответ",
            checklist=["Тестовый пункт"],
        )
        return {
            "status": "healthy",
            "model": getattr(evaluator, "model", "unknown"),
            "base_url": str(evaluator.client.base_url) if evaluator.client else "N/A",
            "test_score": test_result.get("total_score", 0),
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/db/health")
async def db_health_check(db: AsyncSession = Depends(get_db)):
    try:
        from sqlalchemy import text
        result = await db.execute(text("SELECT 1"))
        return {"status": "healthy", "db": "postgresql", "test": result.scalar() == 1}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="BS-Evolve API - Swagger UI")

@app.get("/redoc", include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(openapi_url="/openapi.json", title="BS-Evolve API - ReDoc")

# ---------- Защищённые эндпоинты (требуют авторизации) ----------
@app.post("/cases/select")
async def select_case_for_user(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Выбрать кейс. user_id и role_id берутся из JWT-токена, а не из тела запроса.
    """
    user_id = current_user.user_id
    role_id = current_user.role_id
    competency_id = request.get("competency_id")
    user_level = request.get("user_level", 0.5)

    if not competency_id:
        return {"error": "competency_id required"}

    case = await case_selector.select_case(competency_id, user_level)
    if not case:
        return {"error": "No case available"}

    session_key = f"{user_id}_{competency_id}"
    user_sessions[session_key] = {
        "case_id": case.get("id"),
        "scenario": case.get("scenario"),
        "checklist": case.get("checklist", []),
        "competency_id": competency_id,
        "role_id": role_id,
    }

    return {
        "case_id": case.get("id"),
        "scenario": case.get("scenario"),
        "checklist": case.get("checklist", []),
        "title": case.get("title", ""),
    }

@app.post("/cases/evaluate")
async def evaluate_case(
    request: dict,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Оценить ответ. user_id и role_id берутся из токена.
    """
    user_id = current_user.user_id
    role_id = current_user.role_id
    competency_id = request.get("competency_id")
    answer = request.get("answer", "")

    session_key = f"{user_id}_{competency_id}"
    if session_key not in user_sessions:
        return {"error": "No active case session"}

    session = user_sessions[session_key]

    evaluation = await get_llm_evaluator().evaluate_case(
        scenario=session["scenario"],
        user_answer=answer,
        checklist=session["checklist"]
    )

    evaluation["case_id"] = session["case_id"]
    evaluation["competency_id"] = competency_id
    evaluation["passed"] = evaluation.get("total_score", 0) >= 70

    user_service = UserService(db)
    await user_service.get_or_create_user(user_id, role_id)
    await user_service.save_case_result(
        user_id=user_id,
        case_id=session["case_id"],
        competency_code=competency_id,
        user_answer=answer,
        evaluation_score=evaluation["total_score"],
        evaluation_details=evaluation.get("details", {}),
        passed=evaluation["passed"],
    )

    del user_sessions[session_key]
    return evaluation

# ---------- Запуск ----------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)