"""add_description_to_subjects

Revision ID: 76441a356c59
Revises: 3b295f62ef44
Create Date: 2025-09-30 16:22:19.415436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '76441a356c59'
down_revision: Union[str, None] = '3b295f62ef44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add missing columns to subjects table
    op.add_column('subjects', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('subjects', sa.Column('category', sa.String(length=50), nullable=True, default='programming_fundamentals'))
    op.add_column('subjects', sa.Column('difficulty_level', sa.String(length=20), nullable=True, default='beginner'))
    op.add_column('subjects', sa.Column('estimated_duration', sa.String(length=50), nullable=True))
    op.add_column('subjects', sa.Column('icon_name', sa.String(length=50), nullable=True))
    op.add_column('subjects', sa.Column('color_code', sa.String(length=10), nullable=True))
    op.add_column('subjects', sa.Column('is_active', sa.Boolean(), nullable=True, default=True))
    op.add_column('subjects', sa.Column('order_index', sa.Integer(), nullable=True, default=0))
    op.add_column('subjects', sa.Column('total_problems', sa.Integer(), nullable=True, default=0))
    op.add_column('subjects', sa.Column('total_students', sa.Integer(), nullable=True, default=0))
    op.add_column('subjects', sa.Column('average_completion_rate', sa.Float(), nullable=True, default=0.0))
    op.add_column('subjects', sa.Column('updated_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    # Remove added columns from subjects table
    op.drop_column('subjects', 'updated_at')
    op.drop_column('subjects', 'average_completion_rate')
    op.drop_column('subjects', 'total_students')
    op.drop_column('subjects', 'total_problems')
    op.drop_column('subjects', 'order_index')
    op.drop_column('subjects', 'is_active')
    op.drop_column('subjects', 'color_code')
    op.drop_column('subjects', 'icon_name')
    op.drop_column('subjects', 'estimated_duration')
    op.drop_column('subjects', 'difficulty_level')
    op.drop_column('subjects', 'category')
    op.drop_column('subjects', 'description')
