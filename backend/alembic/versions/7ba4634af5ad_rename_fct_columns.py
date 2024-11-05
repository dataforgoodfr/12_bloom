"""rename_fct_columns

Revision ID: 7ba4634af5ad
Revises: 7921b2e3a780
Create Date: 2024-11-05 21:26:52.687517

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ba4634af5ad'
down_revision = '7921b2e3a780'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("fct_excursion", "total_time_in_costal_waters", new_column_name="total_time_in_zones_with_no_fishing_rights")
    op.alter_column("fct_excursion", "total_time_fishing_in_costal_waters", new_column_name="total_time_fishing_in_zones_with_no_fishing_rights")
    op.alter_column("fct_segment", "in_costal_waters", new_column_name="in_zone_with_no_fishing_rights")


def downgrade() -> None:
    pass
