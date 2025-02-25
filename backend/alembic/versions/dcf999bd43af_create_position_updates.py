"""create_position_updates

Revision ID: dcf999bd43af
Revises: 5801cb8f1af5
Create Date: 2025-02-25 14:58:48.958984

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'dcf999bd43af'
down_revision = '5801cb8f1af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "position_updates",
        sa.Column("id", sa.Integer(), sa.Identity(), primary_key=True, index=True),
        sa.Column(
            "vessel_id", sa.Integer, sa.ForeignKey("dim_vessel.id"), nullable=False
        ),
        sa.Column("point_in_time", sa.DateTime(timezone=True)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
    )


def downgrade() -> None:
    op.drop_table("position_updates")
