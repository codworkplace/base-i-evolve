from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

SYNC_DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(SYNC_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, expire_on_commit=False)


def get_db_sync():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
