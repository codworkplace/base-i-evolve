"""Initial migration

Revision ID: 3959cda54590
Revises: 53ce0cec9d15
Create Date: 2026-05-23 04:20:58.668645

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "3959cda54590"
down_revision: Union[str, Sequence[str], None] = "53ce0cec9d15"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
