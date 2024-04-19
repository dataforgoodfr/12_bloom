"""create_facts

Revision ID: ca6054b36c21
Revises: 4d475167ca65
Create Date: 2024-03-22 22:47:25.004783

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "ca6054b36c21"
down_revision = "4d475167ca65"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "fct_excursion",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("vessel_id", sa.Integer, sa.ForeignKey("dim_vessel.id"), nullable=False),
        sa.Column("departure_port_id", sa.Integer, sa.ForeignKey("dim_port.id")),
        sa.Column("departure_at", sa.DateTime(timezone=True)),
        sa.Column("departure_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")),
        sa.Column("arrival_port_id", sa.Integer, sa.ForeignKey("dim_port.id")),
        sa.Column("arrival_at", sa.DateTime(timezone=True)),
        sa.Column("arrival_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")),
        sa.Column("excursion_duration", sa.Interval),
        sa.Column("total_time_at_sea", sa.Interval),
        sa.Column("total_time_in_amp", sa.Interval),
        sa.Column("total_time_in_territorial_waters", sa.Interval),
        sa.Column("total_time_in_costal_waters", sa.Interval),
        sa.Column("total_time_fishing", sa.Interval),
        sa.Column("total_time_fishing_in_amp", sa.Interval),
        sa.Column("total_time_fishing_in_territorial_waters", sa.Interval),
        sa.Column("total_time_fishing_in_costal_waters", sa.Interval),
        sa.Column("total_time_extincting_amp", sa.Interval),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
    )
    op.create_index("i_fct_excursion_vessel_id", "fct_excursion", ["vessel_id"])
    op.create_index(
        "i_fct_excursion_created_updated", "fct_excursion", ["created_at", "updated_at"]
    )
    op.create_index("i_fct_excursion_arrival_at", "fct_excursion", ["arrival_at"])

    op.create_table(
        "fct_segment",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column(
            "excursion_id",
            sa.Integer,
            sa.ForeignKey("fct_excursion.id"),
            nullable=False,
        ),
        sa.Column("timestamp_start", sa.DateTime(timezone=True)),
        sa.Column("timestamp_end", sa.DateTime(timezone=True)),
        sa.Column("segment_duration", sa.Interval),
        sa.Column("start_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")),
        sa.Column("end_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")),
        sa.Column("heading", sa.Double),
        sa.Column("distance", sa.Double),
        sa.Column("average_speed", sa.Double),
        # sa.Column("speed_at_start", sa.Double),
        # sa.Column("speed_at_end", sa.Double),
        sa.Column("type", sa.String),
        sa.Column("in_amp_zone", sa.Boolean),
        sa.Column("in_territorial_waters", sa.Boolean),
        sa.Column("in_costal_waters", sa.Boolean),
        sa.Column("last_vessel_segment", sa.Boolean),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
    )
    op.create_index("i_fct_segment_excursion_id", "fct_segment", ["excursion_id"])
    op.create_index(
        "i_fct_segment_timestamp", "fct_segment", ["timestamp_start", "timestamp_end"]
    )
    op.create_index(
        "i_fct_segment_created_updated", "fct_segment", ["created_at", "updated_at"]
    )


def downgrade() -> None:
    op.drop_table("fct_segment")
    op.drop_table("fct_excursion")
