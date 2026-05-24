import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base

# Определяем, где мы находимся
ON_RENDER = os.getenv("RENDER") == "true"  # Render сам устанавливает эту переменную

if ON_RENDER:
    # На Render используем PostgreSQL из переменной окружения
    TEST_DATABASE_URL = os.getenv("DATABASE_URL")
    print("🚀 Running on Render with PostgreSQL")
else:
    # Локально используем SQLite
    TEST_DATABASE_URL = "sqlite:///:memory:"
    print("💻 Running locally with SQLite")

sync_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if not ON_RENDER else {},
)
TestingSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


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
