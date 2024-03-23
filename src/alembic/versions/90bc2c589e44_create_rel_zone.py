"""create_rel_zone

Revision ID: 90bc2c589e44
Revises: ca6054b36c21
Create Date: 2024-03-22 23:11:32.911250

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = "90bc2c589e44"
down_revision = "ca6054b36c21"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rel_segment_zone",
        sa.Column("segment_id", sa.Integer, sa.ForeignKey("fct_segment.id"), nullable=False),
        sa.Column("zone_id", sa.Integer, sa.ForeignKey("dim_zone.id"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
    )
    op.create_index("i_segment_zone", "rel_segment_zone", ["segment_id", "zone_id"])


def downgrade() -> None:
    op.drop_table("rel_segment_zone")
