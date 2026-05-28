import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from app.main import app
from app.db.base import Base, get_db

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://bsuser:bspassword@localhost:5432/bsevolve_test")
ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")

# Асинхронный движок для API тестов
async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)
AsyncTestingSessionLocal = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with AsyncTestingSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

# Синхронный движок для прямых запросов в тестах
sync_engine = create_engine(DATABASE_URL)
SyncTestingSessionLocal = sessionmaker(sync_engine, expire_on_commit=False)

# Создаём таблицы
Base.metadata.create_all(bind=sync_engine)

@pytest.fixture
def db_session():
    session = SyncTestingSessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()

@pytest.fixture
def client():
    return TestClient(app)