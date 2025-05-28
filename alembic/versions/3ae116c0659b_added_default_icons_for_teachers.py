"""added default icons for teachers

Revision ID: 3ae116c0659b
Revises: d3a0283e2206
Create Date: 2025-05-29 00:55:17.990067

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

from app.config.config import settings

# revision identifiers, used by Alembic.
revision: str = '3ae116c0659b'
down_revision: Union[str, None] = 'd3a0283e2206'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text("""
                UPDATE teachers
                SET icon = CASE
                    WHEN gender = 'M' THEN :man_icon
                    WHEN gender = 'W' THEN :woman_icon
                    ELSE NULL
                END
                WHERE icon IS NULL
            """),
        {"man_icon": settings.DEFAULT_MAN_ICON, "woman_icon": settings.DEFAULT_WOMAN_ICON}
    )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text("""
                UPDATE teachers
                SET icon = NULL
                WHERE icon IN (:man_icon, :woman_icon)
            """),
        {"man_icon": settings.DEFAULT_MAN_ICON, "woman_icon": settings.DEFAULT_WOMAN_ICON}
    )

