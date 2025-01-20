"""rename some elements

Revision ID: 469e75c471f7
Revises: 467f48c01237
Create Date: 2025-01-19 20:24:31.407561

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '469e75c471f7'
down_revision: Union[str, None] = '467f48c01237'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tags', sa.Column('name', sa.String(), nullable=False))
    op.drop_column('tags', 'tag')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tags', sa.Column('tag', sa.VARCHAR(), autoincrement=False, nullable=False))
    op.drop_column('tags', 'name')
    # ### end Alembic commands ###