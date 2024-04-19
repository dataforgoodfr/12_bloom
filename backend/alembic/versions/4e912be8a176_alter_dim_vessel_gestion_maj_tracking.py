"""alter_dim_vessel_gestion_maj_tracking

Revision ID: 4e912be8a176
Revises: 65a36ee545fe
Create Date: 2024-03-30 10:38:00.015020

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '4e912be8a176'
down_revision = '65a36ee545fe'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("dim_vessel_mmsi_key", "dim_vessel")
    op.drop_column("dim_vessel", "mt_activated")
    op.add_column("dim_vessel", sa.Column("tracking_activated", sa.Boolean, default=False))
    op.add_column("dim_vessel", sa.Column("tracking_status", sa.String))
    # A ce stade, on est certain que les MMSI sont uniques dans la table
    op.execute("update dim_vessel set tracking_activated=true")
    op.execute("update dim_vessel set tracking_activated=false, tracking_status='MMSI null' where mmsi is null")
    op.alter_column("dim_vessel", "tracking_activated", nullable=False)


def downgrade() -> None:
    op.drop_column("dim_vessel", "tracking_status")
    op.drop_column("dim_vessel", "tracking_activated")
    op.create_unique_constraint("dim_vessel_mmsi_key", "dim_vessel", ["mmsi"])
    op.add_column("dim_vessel", sa.Column("mt_activated", sa.Boolean))
