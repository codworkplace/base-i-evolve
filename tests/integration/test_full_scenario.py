import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
import uuid


def test_full_user_journey(client: TestClient, db_session):
    # ... (код из моего последнего сообщения)
