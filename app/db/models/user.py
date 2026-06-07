import enum
from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from app.db.base import Base


class AuthRole(str, enum.Enum):
    """Роль для доступа к API (аутентификация)"""
    USER = "user"
    MANAGER = "manager"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    # Существующие поля
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    role_id = Column(String(50), nullable=False)          # бизнес-роль (например, sales_manager)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Новые поля для аутентификации (все nullable = True для обратной совместимости)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=True)
    auth_role = Column(SQLEnum(AuthRole), default=AuthRole.USER)
    is_active = Column(Boolean, default=True)


class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    competency_code = Column(String(20), nullable=False)
    score = Column(Float, default=0.0)
    confidence = Column(Float, default=0.0)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class DiagnosticResult(Base):
    __tablename__ = "diagnostic_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    competency_code = Column(String(20), nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CaseResult(Base):
    __tablename__ = "case_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), index=True, nullable=False)
    case_id = Column(String(50), nullable=False)
    competency_code = Column(String(20), nullable=False)
    user_answer = Column(String, nullable=False)
    evaluation_score = Column(Float, nullable=False)
    evaluation_details = Column(JSON)
    passed = Column(Integer, default=0)  # 0=false, 1=true
    created_at = Column(DateTime(timezone=True), server_default=func.now())