"""Add performance indexes

Revision ID: e5f6a7b8c9d0
Revises: c3d4e5f6a7b8
Create Date: 2026-01-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add indexes for frequently queried fields."""
    # License: is_active for license status checks
    op.create_index('ix_licenses_is_active', 'licenses', ['is_active'])

    # TimeclockEntry: clock_in for date range queries
    op.create_index('ix_timeclock_entries_clock_in', 'timeclock_entries', ['clock_in'])

    # TimeclockEntry: badge_number for employee filtering
    op.create_index('ix_timeclock_entries_badge_number', 'timeclock_entries', ['badge_number'])

    # RegisteredBrowser: fingerprint_hash for fingerprint lookups
    op.create_index('ix_registered_browsers_fingerprint_hash', 'registered_browsers', ['fingerprint_hash'])

    # RegisteredBrowser: last_seen for session cleanup queries
    op.create_index('ix_registered_browsers_last_seen', 'registered_browsers', ['last_seen'])


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_registered_browsers_last_seen', 'registered_browsers')
    op.drop_index('ix_registered_browsers_fingerprint_hash', 'registered_browsers')
    op.drop_index('ix_timeclock_entries_badge_number', 'timeclock_entries')
    op.drop_index('ix_timeclock_entries_clock_in', 'timeclock_entries')
    op.drop_index('ix_licenses_is_active', 'licenses')
