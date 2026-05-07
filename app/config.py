# config.py

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    USE_REAL_SERVICES = os.getenv("USE_REAL_SERVICES", "False").lower() == "true"
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/app.db")