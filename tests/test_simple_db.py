from sqlalchemy import text


def test_db_query(db_session):
    result = db_session.execute(text("SELECT 1"))
    assert result.scalar() == 1
    print("✅ Запрос к БД работает!")
