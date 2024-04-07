"""create_dim_vessel

Revision ID: 41c412cf8175
Revises: b0b4ce13066d
Create Date: 2024-03-21 15:22:24.011124

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "41c412cf8175"
down_revision = "b0b4ce13066d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dim_vessel",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("mmsi", sa.Integer, unique=True),
        sa.Column("ship_name", sa.String, nullable=False),
        sa.Column("width", sa.Double),
        sa.Column("length", sa.Double),
        sa.Column("country_iso3", sa.String, nullable=False),
        sa.Column("type", sa.String),
        sa.Column("imo", sa.Integer),
        sa.Column("cfr", sa.String),
        sa.Column("registration_number", sa.String),
        sa.Column("external_marking", sa.String),
        sa.Column("ircs", sa.String),
        sa.Column("mt_activated", sa.Boolean, nullable=False),
        sa.Column("home_port_id", sa.Integer, sa.ForeignKey("dim_port.id")),
        sa.Column("comment", sa.String),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now())
    ),
        


def downgrade() -> None:
    op.drop_table("dim_vessel")
