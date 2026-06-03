import pytest
import json
from app.real.case_selector import CaseSelector

@pytest.fixture
def sample_cases():
    """Тестовые данные кейсов"""
    return {
        "SLS-04": [
            {"id": "easy_case", "difficulty": "easy", "scenario": "Easy scenario", "title": "Easy", "checklist": []},
            {"id": "medium_case", "difficulty": "medium", "scenario": "Medium scenario", "title": "Medium", "checklist": []},
            {"id": "hard_case", "difficulty": "hard", "scenario": "Hard scenario", "title": "Hard", "checklist": []}
        ],
        "SLS-07": [
            {"id": "sls07_case", "difficulty": "medium", "scenario": "Another scenario", "title": "Another", "checklist": []}
        ]
    }

@pytest.fixture
def case_selector(tmp_path, sample_cases):
    """Создаёт CaseSelector с временным файлом cases.json"""
    cases_file = tmp_path / "cases.json"
    cases_file.write_text(json.dumps(sample_cases), encoding='utf-8')
    selector = CaseSelector()
    selector.cases_file = cases_file
    selector._load_cases()  # загружаем данные из временного файла
    return selector

@pytest.mark.asyncio
async def test_select_case_easy_difficulty(case_selector):
    """Тест: выбор лёгкого кейса для низкого уровня (user_level < 0.33)"""
    case = await case_selector.select_case("SLS-04", user_level=0.2)
    assert case is not None
    assert case["id"] == "easy_case"

@pytest.mark.asyncio
async def test_select_case_medium_difficulty(case_selector):
    """Тест: выбор среднего кейса для среднего уровня (0.33 <= user_level < 0.66)"""
    case = await case_selector.select_case("SLS-04", user_level=0.5)
    assert case is not None
    # Может вернуть easy или medium (в зависимости от реализации), но не hard
    assert case["difficulty"] in ["easy", "medium"]

@pytest.mark.asyncio
async def test_select_case_hard_difficulty(case_selector):
    """Тест: выбор сложного кейса для высокого уровня (user_level >= 0.66)"""
    case = await case_selector.select_case("SLS-04", user_level=0.9)
    assert case is not None
    assert case["id"] == "hard_case"

@pytest.mark.asyncio
async def test_select_case_not_found(case_selector):
    """Тест: компетенция без кейсов"""
    case = await case_selector.select_case("NON_EXISTENT", user_level=0.5)
    assert case is None

@pytest.mark.asyncio
async def test_select_case_empty_list(case_selector):
    """Тест: компетенция с пустым списком кейсов"""
    case_selector.cases["SLS-04"] = []  # делаем список пустым
    case = await case_selector.select_case("SLS-04", user_level=0.5)
    assert case is None