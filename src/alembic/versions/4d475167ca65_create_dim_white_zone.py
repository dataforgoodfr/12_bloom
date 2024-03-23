"""create_dim_white_zone

Revision ID: 4d475167ca65
Revises: 7d3bd6bf5482
Create Date: 2024-03-22 22:44:53.858393

"""

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry
from sqlalchemy.sql import func
from bloom.config import settings


# revision identifiers, used by Alembic.
revision = "4d475167ca65"
down_revision = "7d3bd6bf5482"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dim_white_zone",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("geometry", Geometry(geometry_type="POLYGON", srid=settings.srid)),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
    )
    op.create_index(
        "i_dim_white_zone_created_updated",
        "dim_white_zone",
        ["created_at", "updated_at"],
    )


def downgrade() -> None:
    op.drop_table("dim_white_zone")
