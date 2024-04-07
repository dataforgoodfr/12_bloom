"""create_vessel_data_tables

Revision ID: 2d54ea045ff3
Revises: 41c412cf8175
Create Date: 2024-03-22 21:48:06.473750

"""

from alembic import op
import sqlalchemy as sa
from bloom.config import settings
from geoalchemy2 import Geometry
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = "2d54ea045ff3"
down_revision = "41c412cf8175"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vessel_positions",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("accuracy", sa.String),
        sa.Column("collection_type", sa.String),
        sa.Column("course", sa.Double),
        sa.Column("heading", sa.Double),
        sa.Column(
            "position", Geometry(geometry_type="POINT", srid=settings.srid), nullable=False
        ),
        sa.Column("latitude", sa.Double),
        sa.Column("longitude", sa.Double),
        sa.Column("maneuver", sa.String),
        sa.Column("navigational_status", sa.String),
        sa.Column("rot", sa.Double),
        sa.Column("speed", sa.Double),
        sa.Column("vessel_id", sa.Integer, sa.ForeignKey("dim_vessel.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    op.create_index("i_vessel_positions_timesamp", "vessel_positions", ["timestamp"])
    op.create_index("i_vessel_positions_vessel_id", "vessel_positions", ["vessel_id"])
    op.create_index("i_vessel_positions_created_updated", "vessel_positions", ["created_at"])

    op.create_table(
        "vessel_data",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ais_class", sa.String),
        sa.Column("flag", sa.String),
        sa.Column("name", sa.String),
        sa.Column("callsign", sa.String),
        sa.Column("ship_type", sa.String),
        sa.Column("sub_ship_type", sa.String),
        sa.Column("mmsi", sa.Integer),
        sa.Column("imo", sa.Integer),
        sa.Column("width", sa.Integer),
        sa.Column("length", sa.Integer),
        sa.Column("vessel_id", sa.Integer, sa.ForeignKey("dim_vessel.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column('comment', sa.String)
    )
    op.create_index("i_vessel_data_timesamp", "vessel_data", ["timestamp"])
    op.create_index("i_vessel_data_vessel_id", "vessel_data", ["vessel_id"])
    op.create_index("i_vessel_data_created_updated", "vessel_data", ["created_at"])

    op.create_table(
        "vessel_voyage",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("destination", sa.String),
        sa.Column("draught", sa.Double),
        sa.Column("eta", sa.DateTime(timezone=True)),
        sa.Column("vessel_id", sa.Integer, sa.ForeignKey("dim_vessel.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    op.create_index("i_vessel_voyage_timesamp", "vessel_data", ["timestamp"])
    op.create_index("i_vessel_voyage_vessel_id", "vessel_data", ["vessel_id"])
    op.create_index("i_vessel_voyage_created_updated", "vessel_data", ["created_at"])


def downgrade() -> None:
    op.drop_table("vessel_positions")
    op.drop_table("vessel_data")
    op.drop_table("vessel_voyage")
