from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.base import get_db
from app.db.models.user import User
from app.core.security import decode_token

security = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    payload = decode_token(creds.credentials)
    if not payload:
        raise HTTPException(401, "Invalid token")
    email = payload.get("sub")
    if not email:
        raise HTTPException(401, "Invalid token payload")
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(401, "User not found or inactive")
    return user

def require_auth_role(required: str):
    def checker(user: User = Depends(get_current_user)):
        if user.auth_role.value != required and user.auth_role.value != "admin":
            raise HTTPException(403, "Insufficient permissions")
        return user
    return checker