from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from app.db.base import get_db
from app.db.models.user import User, AuthRole
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token

router = APIRouter(prefix="/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    password: str
    user_id: str           # публичный идентификатор (может совпадать с email)
    role_id: str = "sales_manager"   # бизнес-роль по умолчанию

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # Проверка email
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")
    # Проверка user_id
    result = await db.execute(select(User).where(User.user_id == req.user_id))
    if result.scalar_one_or_none():
        raise HTTPException(400, "User ID already taken")
    
    hashed = get_password_hash(req.password)
    user = User(
        user_id=req.user_id,
        email=req.email,
        hashed_password=hashed,
        role_id=req.role_id,
        auth_role=AuthRole.USER,
        is_active=True
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    access = create_access_token(data={"sub": user.email, "auth_role": user.auth_role.value, "user_id": user.user_id})
    refresh = create_refresh_token(data={"sub": user.email})
    return {"access_token": access, "refresh_token": refresh}

@router.post("/login")
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(401, "Invalid credentials")
    if not user.is_active:
        raise HTTPException(400, "Inactive user")
    access = create_access_token(data={"sub": user.email, "auth_role": user.auth_role.value, "user_id": user.user_id})
    refresh = create_refresh_token(data={"sub": user.email})
    return {"access_token": access, "refresh_token": refresh}