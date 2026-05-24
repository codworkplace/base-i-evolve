import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db

# Определяем, где мы находимся
ON_RENDER = os.getenv("RENDER") == "true"

if ON_RENDER:
    TEST_DATABASE_URL = os.getenv("DATABASE_URL")
    print("🚀 Running on Render with PostgreSQL")
else:
    # На CI (Linux) и локально (Windows) используем SQLite
    TEST_DATABASE_URL = "sqlite:///:memory:"
    print("💻 Running locally or CI with SQLite")

# Синхронный движок для тестов
sync_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in TEST_DATABASE_URL else {},
)

# ЯВНО СОЗДАЁМ ВСЕ ТАБЛИЦЫ
Base.metadata.create_all(bind=sync_engine)

TestingSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


@pytest.fixture
def client():
    return TestClient(app)
