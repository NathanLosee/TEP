"""Add single active license constraint

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-02-02 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'f6a7b8c9d0e1'
down_revision: Union[str, None] = 'e5f6a7b8c9d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add partial unique index to enforce only one active license."""
    # SQLite supports partial indexes (WHERE clause).
    # This ensures at most one row can have is_active = 1.
    op.execute(
        "CREATE UNIQUE INDEX ix_licenses_single_active "
        "ON licenses (is_active) WHERE is_active = 1"
    )


def downgrade() -> None:
    """Remove single active license constraint."""
    op.drop_index('ix_licenses_single_active', 'licenses')
