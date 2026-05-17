# competencies.py

import json
from pathlib import Path


class CompetenciesStub:
    def __init__(self):
        self.data_path = Path("data/competencies.json")
        self._load_data()

    def _load_data(self):
        with open(self.data_path, "r") as f:
            self.competencies = json.load(f)

    async def get_competency(self, code: str):
        return self.competencies.get(code)

    async def get_competencies_by_role(self, role_id: str):
        """Получить компетенции для роли"""
        from app.stub.roles import RolesStub  # временный импорт

        roles_stub = RolesStub()
        role = await roles_stub.get_role(role_id)
        if not role:
            return []

        comps = []
        for code in role["competencies"]:
            comp = await self.get_competency(code)
            if comp:
                comps.append({"code": code, **comp})
        return comps
