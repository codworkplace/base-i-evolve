"""manual_add_auth_fields

Revision ID: (оставьте тот, что сгенерировался)
Revises: (предыдущий)
Create Date: ...
"""

from alembic import op
import sqlalchemy as sa

# идентификаторы для downgrade – можно не менять

def upgrade():
    # Добавляем колонки, если они ещё не существуют
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [col['name'] for col in inspector.get_columns('users')]
    
    if 'email' not in columns:
        op.add_column('users', sa.Column('email', sa.String(100), nullable=True, unique=True))
        op.create_index('ix_users_email', 'users', ['email'], unique=True)
    
    if 'hashed_password' not in columns:
        op.add_column('users', sa.Column('hashed_password', sa.String(255), nullable=True))
    
    if 'auth_role' not in columns:
        op.add_column('users', sa.Column('auth_role', sa.Enum('user', 'manager', 'admin', name='authrole'), nullable=True, server_default='user'))
    
    if 'is_active' not in columns:
        op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=True, server_default='t'))

def downgrade():
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'auth_role')
    op.drop_column('users', 'hashed_password')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_column('users', 'email')