from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.models import User, UserSkill, DiagnosticResult


class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

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

        # Обновляем user_skills
        await self._update_skill(user_id, competency_code, score / 100)

    async def _update_skill(self, user_id: str, competency_code: str, new_score: float):
        result = await self.db.execute(
            select(UserSkill).where(
                UserSkill.user_id == user_id,
                UserSkill.competency_code == competency_code,
            )
        )
        skill = result.scalar_one_or_none()

        if skill:
            # moving average
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
