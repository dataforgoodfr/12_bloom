"""rename_total_time_extincting_amp

Revision ID: 7921b2e3a780
Revises: 384baeb90009
Create Date: 2024-11-01 21:26:02.906937

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7921b2e3a780'
down_revision = '384baeb90009'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("fct_excursion", "total_time_extincting_amp", new_column_name="total_time_default_ais")


def downgrade() -> None:
    pass
