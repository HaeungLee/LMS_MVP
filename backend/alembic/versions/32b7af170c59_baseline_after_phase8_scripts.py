"""baseline_after_phase8_scripts

Revision ID: 32b7af170c59
Revises: b056eb6131d9
Create Date: 2025-09-02 17:15:25.640561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '32b7af170c59'
down_revision: Union[str, None] = 'b056eb6131d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
