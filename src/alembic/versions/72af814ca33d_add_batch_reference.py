"""add batch reference

Revision ID: 72af814ca33d
Revises: 4e912be8a176
Create Date: 2024-04-03 21:45:21.431765

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72af814ca33d'
down_revision = '4e912be8a176'
branch_labels = None
depends_on = '4e912be8a176'


def upgrade() -> None:
    op.add_column('dim_vessel',sa.Column("batch", sa.String),schema='public')
    op.add_column('spire_ais_data',sa.Column("batch", sa.String),
                                             schema='public')
    op.rename_table('spire_ais_data','stg_spire_ais_data',schema='public')
    pass


def downgrade() -> None:
    op.rename_table('stg_spire_ais_data','spire_ais_data',schema='public')
    op.drop_column('spire_ais_data','batch',schema='public')
    op.drop_column('dim_vessel','batch',schema='public')
    pass
