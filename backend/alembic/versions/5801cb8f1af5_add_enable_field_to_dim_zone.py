"""add enable field to dim_zone

Revision ID: 5801cb8f1af5
Revises: 5bfe00a08853
Create Date: 2024-12-17 22:28:50.714813

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5801cb8f1af5'
down_revision = '5bfe00a08853'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    This evolution was motivated by the fact that some areas are PMA but contains
    some ports that are not registered. This leads to incorrect vessel activity
    The solution proposed here is to add enable column to dim_zone and fct_metrics
    to be able to choose if theses zone are took in account in aggregations or not
    even if they are present and calculated

    """
    # add column enable 
    op.add_column("dim_zone",sa.Column("enable",sa.Boolean(),nullable=False,default=True, server_default="True"))
    op.add_column("fct_metrics",sa.Column("zone_enable",sa.Boolean(),nullable=False,default=True, server_default="True"))
    pass


def downgrade() -> None:
    op.drop_column("fct_metrics","zone_enable")
    op.drop_column("dim_zone","enable")
    pass
