# roles.py

import json
from pathlib import Path


class RolesStub:
    def __init__(self):
        self.data_path = Path("data/roles.json")
        self._load_data()

    def _load_data(self):
        with open(self.data_path, "r") as f:
            self.roles = json.load(f)

    async def get_role(self, role_id: str):
        """Получить роль по ID"""
        if role_id in self.roles:
            return {"id": role_id, **self.roles[role_id]}
        return None

    async def list_roles(self):
        """Список всех ролей"""
        return [{"id": k, "name": v["name"]} for k, v in self.roles.items()]
