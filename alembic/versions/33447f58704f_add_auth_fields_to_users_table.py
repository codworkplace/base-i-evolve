"""Add auth fields to users table

Revision ID: 33447f58704f
Revises: 3959cda54590
Create Date: 2026-06-07 03:24:41.926455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33447f58704f'
down_revision: Union[str, Sequence[str], None] = '3959cda54590'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
