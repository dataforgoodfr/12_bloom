"""modification cle primaire sur fct_metrics

Revision ID: 5bfe00a08853
Revises: 2b9d9e61be30
Create Date: 2024-12-12 18:19:03.128908

"""
from typing import List
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5bfe00a08853'
down_revision = '2b9d9e61be30'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("fct_metrics_pkey", "fct_metrics", type_="primary")
    op.create_primary_key(
        "fct_metrics_pkey", "fct_metrics", columns=["timestamp", "vessel_id", "zone_id"]
    )

def downgrade() -> None:
    op.drop_constraint("fct_metrics_pkey", "fct_metrics", type_="primary")
    op.create_primary_key("fct_metrics_pkey", "fct_metrics", columns=["timestamp", "vessel_id", "zone_name"])
