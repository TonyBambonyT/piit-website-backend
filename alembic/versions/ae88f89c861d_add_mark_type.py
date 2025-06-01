"""add mark type

Revision ID: ae88f89c861d
Revises: 3ae116c0659b
Create Date: 2025-06-01 21:15:26.600035

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae88f89c861d'
down_revision: Union[str, None] = '3ae116c0659b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('curriculum_units', sa.Column('mark_type', sa.String(), nullable=True))
    op.execute("UPDATE curriculum_units SET mark_type = 'unspecified' WHERE mark_type IS NULL")
    op.alter_column('curriculum_units', 'mark_type', nullable=False)


def downgrade() -> None:
    op.drop_column('curriculum_units', 'mark_type')
