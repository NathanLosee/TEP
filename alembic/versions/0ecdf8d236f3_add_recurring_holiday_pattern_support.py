"""Add recurring holiday pattern support

Revision ID: 0ecdf8d236f3
Revises: 6f5391cead75
Create Date: 2026-01-05 21:13:08.856818

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0ecdf8d236f3'
down_revision: Union[str, None] = '6f5391cead75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table("holidays", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "is_recurring",
                sa.Boolean(),
                nullable=False,
                server_default="0",
            )
        )
        batch_op.add_column(
            sa.Column("recurrence_type", sa.String(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("recurrence_month", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("recurrence_day", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("recurrence_week", sa.Integer(), nullable=True)
        )
        batch_op.add_column(
            sa.Column("recurrence_weekday", sa.Integer(), nullable=True)
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("holidays", schema=None) as batch_op:
        batch_op.drop_column("recurrence_weekday")
        batch_op.drop_column("recurrence_week")
        batch_op.drop_column("recurrence_day")
        batch_op.drop_column("recurrence_month")
        batch_op.drop_column("recurrence_type")
        batch_op.drop_column("is_recurring")
