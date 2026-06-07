from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.db.models import User, UserSkill, DiagnosticResult, CaseResult
from app.db.models.user import AuthRole   # импорт новой роли
import structlog
from typing import Optional

logger = structlog.get_logger()


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ---------- Существующие методы (без изменений) ----------
    async def get_or_create_user(self, user_id: str, role_id: str) -> User:
        result = await self.db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            user = User(user_id=user_id, role_id=role_id)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)

        return user

    async def save_diagnostic_score(
        self, user_id: str, competency_code: str, score: float
    ):
        diagnostic = DiagnosticResult(
            user_id=user_id, competency_code=competency_code, score=score
        )
        self.db.add(diagnostic)
        await self.db.commit()

        await self._update_skill(user_id, competency_code, score / 100)

    async def save_case_result(
        self,
        user_id: str,
        case_id: str,
        competency_code: str,
        user_answer: str,
        evaluation_score: float,
        evaluation_details: dict,
        passed: bool,
    ):
        case_result = CaseResult(
            user_id=user_id,
            case_id=case_id,
            competency_code=competency_code,
            user_answer=user_answer,
            evaluation_score=evaluation_score,
            evaluation_details=evaluation_details,
            passed=1 if passed else 0,
        )
        self.db.add(case_result)
        await self.db.commit()

        logger.info(
            "case_result_saved",
            user_id=user_id,
            case_id=case_id,
            competency_code=competency_code,
            score=evaluation_score,
            passed=passed,
        )

        await self._update_skill(user_id, competency_code, evaluation_score / 100)

    async def _update_skill(self, user_id: str, competency_code: str, new_score: float):
        result = await self.db.execute(
            select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.competency_code == competency_code,
            )
        )
        skill = result.scalar_one_or_none()

        if skill:
            skill.score = skill.score * 0.7 + new_score * 0.3
            skill.confidence = min(skill.confidence + 0.1, 1.0)
        else:
            skill = UserSkill(
                user_id=user_id,
                competency_code=competency_code,
                score=new_score,
                confidence=0.1,
            )
            self.db.add(skill)

        await self.db.commit()

    # ---------- Новые методы для аутентификации и администрирования ----------
    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_user_by_public_id(self, public_id: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.user_id == public_id))
        return result.scalar_one_or_none()

    async def create_auth_user(
        self,
        email: str,
        hashed_password: str,
        user_id: str,
        role_id: str = "sales_manager",
        auth_role: AuthRole = AuthRole.USER,
    ) -> User:
        """Создаёт пользователя с email и паролем (для регистрации)."""
        user = User(
            email=email,
            hashed_password=hashed_password,
            user_id=user_id,
            role_id=role_id,
            auth_role=auth_role,
            is_active=True,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def update_auth_role(self, user_id: int, new_role: AuthRole) -> bool:
        result = await self.db.execute(
            update(User).where(User.id == user_id).values(auth_role=new_role)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def set_password(self, user_id: int, hashed_password: str) -> bool:
        result = await self.db.execute(
            update(User).where(User.id == user_id).values(hashed_password=hashed_password)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def activate_user(self, user_id: int) -> bool:
        result = await self.db.execute(
            update(User).where(User.id == user_id).values(is_active=True)
        )
        await self.db.commit()
        return result.rowcount > 0

    async def deactivate_user(self, user_id: int) -> bool:
        result = await self.db.execute(
            update(User).where(User.id == user_id).values(is_active=False)
        )
        await self.db.commit()
        return result.rowcount > 0