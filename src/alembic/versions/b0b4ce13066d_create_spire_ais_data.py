"""create_spire_ais_data

Revision ID: b0b4ce13066d
Revises: 7962eee40abe
Create Date: 2024-03-18 21:13:15.360347

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "b0b4ce13066d"
down_revision = "7962eee40abe"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "spire_ais_data",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("spire_update_statement", sa.DateTime(timezone=True)),
        sa.Column("vessel_ais_class", sa.String),
        sa.Column("vessel_flag", sa.String),
        sa.Column("vessel_name", sa.String),
        sa.Column("vessel_callsign", sa.String),
        sa.Column("vessel_timestamp", sa.DateTime(timezone=True)),
        sa.Column("vessel_update_timestamp", sa.DateTime(timezone=True)),
        sa.Column("vessel_ship_type", sa.String),
        sa.Column("vessel_sub_ship_type", sa.String),
        sa.Column("vessel_mmsi", sa.Integer),
        sa.Column("vessel_imo", sa.Integer),
        sa.Column("vessel_width", sa.Integer),
        sa.Column("vessel_length", sa.Integer),
        sa.Column("position_accuracy", sa.String),
        sa.Column("position_collection_type", sa.String),
        sa.Column("position_course", sa.Double),
        sa.Column("position_heading", sa.Double),
        sa.Column("position_latitude", sa.Double),
        sa.Column("position_longitude", sa.Double),
        sa.Column("position_maneuver", sa.String),
        sa.Column("position_navigational_status", sa.String),
        sa.Column("position_rot", sa.Double),
        sa.Column("position_speed", sa.Double),
        sa.Column("position_timestamp", sa.DateTime(timezone=True)),
        sa.Column("position_update_timestamp", sa.DateTime(timezone=True)),
        sa.Column("voyage_destination", sa.String),
        sa.Column("voyage_draught", sa.Double),
        sa.Column("voyage_eta", sa.DateTime(timezone=True)),
        sa.Column("voyage_timestamp", sa.DateTime(timezone=True)),
        sa.Column("voyage_update_timestamp", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now()),
    )

    op.create_index("i_spire_ais_data_vessel_timesamp", "spire_ais_data", ["vessel_timestamp"])
    op.create_index(
        "i_spire_ais_data_position_timesamp", "spire_ais_data", ["position_timestamp"]
    )
    op.create_index("i_spire_ais_data_voyage_timesamp", "spire_ais_data", ["voyage_timestamp"])


def downgrade() -> None:
    op.drop_table("spire_ais_data")
