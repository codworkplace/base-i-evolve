# case_selector.py

import json
from pathlib import Path


class CaseSelector:
    def __init__(self):
        self.cases_file = Path("data/cases.json")
        self._load_cases()

    def _load_cases(self):
        if self.cases_file.exists():
            with open(self.cases_file, "r", encoding="utf-8") as f:
                self.cases = json.load(f)
        else:
            self.cases = {}

    async def select_case(self, competency_id: str, user_level: float = 0.5):
        """Выбирает кейс подходящей сложности"""

        if competency_id not in self.cases:
            return None

        available_cases = self.cases[competency_id]

        # Если нет кейсов
        if not available_cases:
            return None

        # Выбираем кейс по уровню сложности
        if user_level < 0.4:
            # Низкий уровень - простые кейсы
            suitable = [
                c for c in available_cases if c.get("difficulty", "medium") == "easy"
            ]
        elif user_level < 0.7:
            # Средний уровень
            suitable = [
                c
                for c in available_cases
                if c.get("difficulty", "medium") in ["easy", "medium"]
            ]
        else:
            # Высокий уровень - сложные кейсы
            suitable = [
                c for c in available_cases if c.get("difficulty", "medium") == "hard"
            ]

        if not suitable:
            suitable = available_cases

        # Берем первый подходящий
        return suitable[0]
