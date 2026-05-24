"""Initial migration: users and results tables

Revision ID: 53ce0cec9d15
Revises:
Create Date: 2026-05-23 01:46:01.013744

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "53ce0cec9d15"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
