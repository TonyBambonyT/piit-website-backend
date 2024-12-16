"""Create teachers table

Revision ID: e529e9fe560a
Revises: 3ef7ac225555
Create Date: 2024-12-17 00:10:55.076510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e529e9fe560a'
down_revision: Union[str, None] = '3ef7ac225555'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('teachers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('academic_degree', sa.String(), nullable=True),
    sa.Column('department_id', sa.Integer(), nullable=False),
    sa.Column('department_leader', sa.Boolean(), nullable=True),
    sa.Column('department_part_time_job_ids', sa.ARRAY(sa.Integer()), nullable=True),
    sa.Column('department_secretary', sa.Boolean(), nullable=True),
    sa.Column('firstname', sa.String(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('middlename', sa.String(), nullable=True),
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('rank', sa.String(), nullable=False),
    sa.Column('rank_short', sa.String(), nullable=True),
    sa.Column('surname', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('teachers')
    # ### end Alembic commands ###