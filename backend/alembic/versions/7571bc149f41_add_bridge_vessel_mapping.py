"""add bridge vessel mapping

Revision ID: 7571bc149f41
Revises: 5801cb8f1af5
Create Date: 2025-02-06 23:16:09.122359

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '7571bc149f41'
down_revision = '5801cb8f1af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("brg_vessel_mapping",
                    sa.Column("id", sa.Integer, primary_key=True),
                    sa.Column("mmsi", sa.String, nullable=True),
                    sa.Column("imo", sa.Integer, nullable=True),
                    sa.Column("ship_name", sa.String, nullable=True),
                    sa.Column(
                        "vessel_id",
                        sa.Integer,
                        sa.ForeignKey("dim_vessel.id"),
                        nullable=True,
                    ),
                    sa.Column(
                        "created_at",
                        sa.DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now(),
                    ),
                    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
                    )


def downgrade() -> None:
    op.drop_table("brg_vessel_mapping")
    pass
