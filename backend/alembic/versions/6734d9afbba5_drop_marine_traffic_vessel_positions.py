"""drop_marine_traffic_vessel_positions

Revision ID: 6734d9afbba5
Revises: 961cee5426d6
Create Date: 2024-03-09 16:36:32.902469

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6734d9afbba5'
down_revision = '961cee5426d6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_table("marine_traffic_vessel_positions")


def downgrade() -> None:
    pass
