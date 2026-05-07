# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
from pathlib import Path

app = FastAPI(title="BS-Evolve API")

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)