import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base, get_db

ON_RENDER = os.getenv("RENDER") == "true"

if ON_RENDER:
    TEST_DATABASE_URL = os.getenv("DATABASE_URL")
    print("🚀 Running on Render with PostgreSQL")
else:
    TEST_DATABASE_URL = "sqlite:///:memory:"
    print("💻 Running locally with SQLite")

sync_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False} if not ON_RENDER else {},
)
TestingSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Создаёт таблицы ПЕРЕД каждым тестом"""
    # Импортируем модели, чтобы Base их увидел

    Base.metadata.create_all(bind=sync_engine)
    yield
    Base.metadata.drop_all(bind=sync_engine)


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
