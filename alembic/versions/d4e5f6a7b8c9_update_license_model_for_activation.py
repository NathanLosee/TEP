"""Update license model for activation-based licensing

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-01-21 14:00:00.000000

This migration updates the licenses table to support the new activation flow:
- Adds activation_key column (stores the signed proof from license server)
- Removes server_id column (no longer needed, machine binding is in activation_key)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - add activation_key, remove server_id."""
    with op.batch_alter_table('licenses', schema=None) as batch_op:
        # Add activation_key column (required for new licenses)
        # Existing licenses will need to be re-activated
        batch_op.add_column(
            sa.Column('activation_key', sa.String(), nullable=True)
        )
        # Remove server_id column (no longer used)
        batch_op.drop_column('server_id')

    # Mark any existing licenses as inactive since they need re-activation
    # with the new activation flow
    op.execute("UPDATE licenses SET is_active = 0 WHERE activation_key IS NULL")


def downgrade() -> None:
    """Downgrade schema - remove activation_key, add server_id."""
    with op.batch_alter_table('licenses', schema=None) as batch_op:
        # Add server_id column back
        batch_op.add_column(
            sa.Column('server_id', sa.String(), nullable=True)
        )
        # Remove activation_key column
        batch_op.drop_column('activation_key')
