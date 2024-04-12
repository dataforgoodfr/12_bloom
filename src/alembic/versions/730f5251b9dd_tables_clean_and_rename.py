"""tables_clean_and_rename

Revision ID: 730f5251b9dd
Revises: 4e912be8a176
Create Date: 2024-04-05 15:00:40.225950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '730f5251b9dd'
down_revision = '4e912be8a176'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table('spire_ais_data', 'stg_spire_ais_data')
    # rename mpa_fr_with_mn with drop to manually drop it
    op.rename_table('mpa_fr_with_mn', 'drop_mpa_fr_with_mn')
    pass


def downgrade() -> None:
    # nothing to do if drop_mpa_fr_with_mn has been manually dropped
    op.execute('ALTER TABLE IF EXISTS drop_mpa_fr_with_mn RENAME TO mpa_fr_with_mn')
    op.rename_table('stg_spire_ais_data', 'spire_ais_data')
    pass
