"""Create system_settings table

Revision ID: c3d4e5f6a7b8
Revises: 720a5d22f5cc
Create Date: 2026-01-21 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "720a5d22f5cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create system_settings table."""
    op.create_table(
        "system_settings",
        sa.Column("id", sa.Integer(), nullable=False, default=1),
        sa.Column(
            "primary_color",
            sa.String(7),
            nullable=False,
            server_default="#4CAF50",
        ),
        sa.Column(
            "secondary_color",
            sa.String(7),
            nullable=False,
            server_default="#81C784",
        ),
        sa.Column(
            "accent_color",
            sa.String(7),
            nullable=False,
            server_default="#FFEB3B",
        ),
        sa.Column("logo_data", sa.LargeBinary(), nullable=True),
        sa.Column("logo_mime_type", sa.String(50), nullable=True),
        sa.Column("logo_filename", sa.String(255), nullable=True),
        sa.Column(
            "company_name",
            sa.String(255),
            nullable=False,
            server_default="TAP Timeclock",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Insert the default settings row (singleton pattern)
    op.execute(
        "INSERT INTO system_settings (id, primary_color, secondary_color, accent_color, company_name) "
        "VALUES (1, '#4CAF50', '#81C784', '#FFEB3B', 'TAP Timeclock')"
    )


def downgrade() -> None:
    """Drop system_settings table."""
    op.drop_table("system_settings")
