import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db  # 👈 добавить get_db

# Определяем, где мы находимся
ON_RENDER = os.getenv("RENDER") == "true"

if ON_RENDER:
    TEST_DATABASE_URL = os.getenv("DATABASE_URL")
    print("🚀 Running on Render with PostgreSQL")
else:
    TEST_DATABASE_URL = "sqlite:///:memory:"
    print("💻 Running locally with SQLite")

# Синхронный движок для тестов
sync_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if not ON_RENDER else {},
)
TestingSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


# 👇 НОВЫЙ КОД: Переопределяем зависимость get_db для тестов
async def override_get_db():
    """Использует синхронную сессию в асинхронной обёртке для тестов"""

    def _get_sync_session():
        return TestingSessionLocal()

    # Оборачиваем синхронную сессию в асинхронную
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


app.dependency_overrides[get_db] = override_get_db
# 👆 КОНЕЦ НОВОГО КОДА


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=sync_engine)
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()
        Base.metadata.drop_all(bind=sync_engine)


@pytest.fixture
def client():
    return TestClient(app)
