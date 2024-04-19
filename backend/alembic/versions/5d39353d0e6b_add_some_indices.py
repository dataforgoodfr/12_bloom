"""add_some_indices

Revision ID: 5d39353d0e6b
Revises: 2d54ea045ff3
Create Date: 2024-03-22 21:56:47.205061

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5d39353d0e6b"
down_revision = "2d54ea045ff3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("i_spire_ais_data_vessel_mmsi", "spire_ais_data", ["vessel_mmsi"])
    op.create_index("i_spire_ais_data_created_at", "spire_ais_data", ["created_at"])
    op.create_index("i_dim_vessel_created_updated", "dim_vessel", ["created_at", "updated_at"])
    op.create_index("i_dim_port_created_updated", "dim_port", ["created_at", "updated_at"])


def downgrade() -> None:
    op.drop_index("i_spire_ais_data_vessel_mmsi")
    op.drop_index("i_spire_ais_data_created_at")
    op.drop_index("i_dim_vessel_created_updated")
    op.drop_index("i_dim_port_created_updated")
