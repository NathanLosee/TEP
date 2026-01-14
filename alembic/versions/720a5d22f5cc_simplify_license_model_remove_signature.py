"""simplify_license_model_remove_signature

Revision ID: 720a5d22f5cc
Revises: b2c3d4e5f6a7
Create Date: 2026-01-12 12:37:41.461679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '720a5d22f5cc'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - remove signature column from licenses table."""
    # The signature column is no longer needed as the license_key IS the signature
    with op.batch_alter_table('licenses', schema=None) as batch_op:
        batch_op.drop_column('signature')


def downgrade() -> None:
    """Downgrade schema - add signature column back to licenses table."""
    with op.batch_alter_table('licenses', schema=None) as batch_op:
        batch_op.add_column(sa.Column('signature', sa.VARCHAR(), nullable=True))
