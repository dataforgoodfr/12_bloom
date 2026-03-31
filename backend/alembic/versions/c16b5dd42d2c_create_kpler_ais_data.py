"""create_kpler_ais_data

Revision ID: c16b5dd42d2c
Revises: 5801cb8f1af5
Create Date: 2026-03-31 11:43:44.681915

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = 'c16b5dd42d2c'
down_revision = '5801cb8f1af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "kpler_ais_data",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("position_id", sa.Integer),
        sa.Column("vessel_uid", sa.Integer),
        sa.Column("vessel_flag", sa.String),
        sa.Column("vessel_name", sa.String),
        sa.Column("vessel_callsign", sa.String),
        sa.Column("vessel_mmsi", sa.Integer),
        sa.Column("vessel_imo", sa.Integer),
        sa.Column("vessel_marinetraffic_type", sa.String),
        sa.Column("vessel_ais_type", sa.Integer),
        sa.Column("vessel_width", sa.Double),
        sa.Column("vessel_length", sa.Double),
        sa.Column("vessel_grt", sa.Double),
        sa.Column("vessel_dwt", sa.Double),
        sa.Column("static_timestamp", sa.DateTime(timezone=True)),
        sa.Column("static_source", sa.String),
        sa.Column("static_message_type", sa.Integer),
        sa.Column("position_message_type", sa.Integer),
        sa.Column("position_source", sa.String),
        sa.Column("position_course", sa.Double),
        sa.Column("position_heading", sa.Double),
        sa.Column("position_longitude", sa.Double),
        sa.Column("position_latitude", sa.Double),
        sa.Column("position_navigational_status", sa.Integer),
        sa.Column("position_rot", sa.Double),
        sa.Column("position_speed", sa.Double),
        sa.Column("position_timestamp", sa.DateTime(timezone=True)),
        sa.Column("position_kpler_insert_timestamp", sa.DateTime(timezone=True)),
        sa.Column("voyage_destination", sa.String),
        sa.Column("voyage_draught", sa.Double),
        sa.Column("voyage_eta", sa.DateTime(timezone=True)),
        sa.Column("payload", JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=func.now())
    )

    op.create_index("i_kpler_ais_data_static_timesamp", "kpler_ais_data", ["static_timestamp"])
    op.create_index(
        "i_kpler_ais_data_position_timesamp",
        "kpler_ais_data",
        ["position_timestamp"],
    )


def downgrade() -> None:
    op.drop_table("kpler_ais_data")
