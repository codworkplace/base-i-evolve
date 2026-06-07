from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.db.models.user import User, AuthRole
from app.dependencies.auth import require_auth_role
import json
from pathlib import Path

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_auth_role("admin"))])

# --- УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ ---
@router.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "user_id": u.user_id, "role_id": u.role_id, "auth_role": u.auth_role.value} for u in users]

@router.put("/users/{user_id}/role")
async def change_user_role(user_id: int, role: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(404, "User not found")
    if role not in [r.value for r in AuthRole]:
        raise HTTPException(400, "Invalid role")
    user.auth_role = AuthRole(role)
    await db.commit()
    return {"message": "Role updated"}

# --- УПРАВЛЕНИЕ КЕЙСАМИ (через JSON) ---
CASES_FILE = Path("data/cases.json")

def load_cases():
    with open(CASES_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_cases(cases):
    with open(CASES_FILE, "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)

@router.get("/cases")
async def list_cases():
    return load_cases()

@router.post("/cases")
async def create_case(case: dict):
    cases = load_cases()
    comp_id = case["competency_id"]
    new_id = f"{comp_id}_{len(cases.get(comp_id, [])) + 1}"
    new_case = {
        "id": new_id,
        "title": case["title"],
        "difficulty": case["difficulty"],
        "scenario": case["scenario"],
        "checklist": case["checklist"]
    }
    if comp_id not in cases:
        cases[comp_id] = []
    cases[comp_id].append(new_case)
    save_cases(cases)
    return {"message": "Case created", "case_id": new_id}

@router.delete("/cases/{comp_id}/{case_id}")
async def delete_case(comp_id: str, case_id: str):
    cases = load_cases()
    if comp_id not in cases:
        raise HTTPException(404, "Competency not found")
    cases[comp_id] = [c for c in cases[comp_id] if c["id"] != case_id]
    save_cases(cases)
    return {"message": "Case deleted"}