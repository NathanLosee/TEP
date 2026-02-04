"""Add performance indexes

Revision ID: e5f6a7b8c9d0
Revises: c3d4e5f6a7b8
Create Date: 2026-01-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'd4e5f6a7b8c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for frequently queried fields.

    Uses raw SQL with IF NOT EXISTS for idempotency, since some
    indexes may already exist from model-level index=True definitions.
    """
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_licenses_is_active "
        "ON licenses (is_active)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_timeclock_clock_in "
        "ON timeclock (clock_in)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_timeclock_badge_number "
        "ON timeclock (badge_number)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS "
        "ix_registered_browsers_fingerprint_hash "
        "ON registered_browsers (fingerprint_hash)"
    )
    op.execute(
        "CREATE INDEX IF NOT EXISTS "
        "ix_registered_browsers_last_seen "
        "ON registered_browsers (last_seen)"
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_registered_browsers_last_seen', 'registered_browsers')
    op.drop_index('ix_registered_browsers_fingerprint_hash', 'registered_browsers')
    op.drop_index('ix_timeclock_badge_number', 'timeclock')
    op.drop_index('ix_timeclock_clock_in', 'timeclock')
    op.drop_index('ix_licenses_is_active', 'licenses')
