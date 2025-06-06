"""Add new relationships

Revision ID: 05e8b7414130
Revises: 79e030ec5aac
Create Date: 2025-04-04 22:11:01.949306

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05e8b7414130'
down_revision: Union[str, None] = '79e030ec5aac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'stud_groups', ['brs_id'])
    op.create_unique_constraint(None, 'subjects', ['brs_id'])
    op.create_unique_constraint(None, 'teachers', ['brs_id'])
    op.create_foreign_key(None, 'curriculum_units', 'teachers', ['teacher_brs_id'], ['brs_id'])
    op.create_foreign_key(None, 'curriculum_units', 'subjects', ['subject_brs_id'], ['brs_id'])
    op.create_foreign_key(None, 'curriculum_units', 'stud_groups', ['stud_group_brs_id'], ['brs_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'curriculum_units', type_='foreignkey')
    op.drop_constraint(None, 'curriculum_units', type_='foreignkey')
    op.drop_constraint(None, 'curriculum_units', type_='foreignkey')
    op.drop_constraint(None, 'teachers', type_='unique')
    op.drop_constraint(None, 'subjects', type_='unique')
    op.drop_constraint(None, 'stud_groups', type_='unique')
    # ### end Alembic commands ###
