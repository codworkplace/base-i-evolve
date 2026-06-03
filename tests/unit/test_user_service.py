import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import UserService
from app.db.models import User, UserSkill, DiagnosticResult, CaseResult


@pytest.mark.asyncio
async def test_get_or_create_user_existing():
    """Тест: получение существующего пользователя"""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_user = User(user_id="test_user", role_id="sales_manager")

    # scalar_one_or_none — синхронный метод
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=mock_user)
    mock_session.execute = AsyncMock(return_value=mock_result)

    service = UserService(mock_session)
    user = await service.get_or_create_user("test_user", "sales_manager")

    assert user.user_id == "test_user"
    assert user.role_id == "sales_manager"
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_get_or_create_user_new():
    """Тест: создание нового пользователя"""
    mock_session = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)

    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    service = UserService(mock_session)
    user = await service.get_or_create_user("new_user", "sales_manager")

    assert user.user_id == "new_user"
    assert user.role_id == "sales_manager"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_skill_existing():
    """Тест: обновление существующего навыка (moving average)"""
    mock_session = AsyncMock(spec=AsyncSession)

    existing_skill = UserSkill(
        user_id="test_user",
        competency_code="SLS-04",
        score=0.5,
        confidence=0.5
    )

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=existing_skill)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()

    service = UserService(mock_session)
    await service._update_skill("test_user", "SLS-04", 0.9)

    # moving average: 0.5 * 0.7 + 0.9 * 0.3 = 0.62
    assert abs(existing_skill.score - 0.62) < 0.01
    assert existing_skill.confidence == 0.6  # 0.5 + 0.1
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_skill_new():
    """Тест: создание нового навыка"""
    mock_session = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    service = UserService(mock_session)
    await service._update_skill("test_user", "SLS-04", 0.75)

    mock_session.add.assert_called_once()
    added_skill = mock_session.add.call_args[0][0]
    assert added_skill.user_id == "test_user"
    assert added_skill.competency_code == "SLS-04"
    assert added_skill.score == 0.75
    assert added_skill.confidence == 0.1
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_save_case_result():
    """Тест: сохранение результата кейса"""
    mock_session = AsyncMock(spec=AsyncSession)

    # Мокаем execute для _update_skill
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    service = UserService(mock_session)
    await service.save_case_result(
        user_id="test_user",
        case_id="case_001",
        competency_code="SLS-04",
        user_answer="Test answer",
        evaluation_score=85.0,
        evaluation_details={"total_score": 85, "passed": True},
        passed=True
    )

    # add вызывается дважды: сначала CaseResult, потом UserSkill
    assert mock_session.add.call_count == 2
    first_call_args = mock_session.add.call_args_list[0][0][0]
    assert isinstance(first_call_args, CaseResult)
    assert first_call_args.user_id == "test_user"
    assert first_call_args.case_id == "case_001"
    assert first_call_args.evaluation_score == 85.0

    assert mock_session.commit.call_count >= 1