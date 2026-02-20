"""Initial migration - create users table

Revision ID: 001_initial
Revises: 
Create Date: 2026-01-28

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=True),
        sa.Column('tg_id', sa.BigInteger(), nullable=False),
        sa.Column('soft_currency', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('hard_currency', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('experience', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('level', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('energy', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('max_energy', sa.Integer(), nullable=False, server_default='100'),
        sa.Column('energy_last_update', sa.DateTime(), nullable=True),
        sa.Column('energy_notification_sent', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('tutorial_step', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_activity', sa.DateTime(), nullable=True),
        sa.Column('settings_data', sa.JSON(), nullable=True),
        sa.Column('game_data', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_tg_id', 'users', ['tg_id'], unique=True)


def downgrade() -> None:
    op.drop_index('ix_users_tg_id', table_name='users')
    op.drop_table('users')
