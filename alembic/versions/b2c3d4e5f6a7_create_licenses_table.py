"""Create licenses table

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-01-11 16:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'licenses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('license_key', sa.String(), nullable=False),
        sa.Column('signature', sa.String(), nullable=False),
        sa.Column('activated_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('server_id', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('license_key')
    )
    # Create index on license_key for faster lookups
    op.create_index(op.f('ix_licenses_license_key'), 'licenses', ['license_key'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_licenses_license_key'), table_name='licenses')
    op.drop_table('licenses')
