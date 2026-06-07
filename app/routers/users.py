from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user
from app.db.models.user import User

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "user_id": current_user.user_id,
        "email": current_user.email,
        "role_id": current_user.role_id,
        "auth_role": current_user.auth_role.value
    }