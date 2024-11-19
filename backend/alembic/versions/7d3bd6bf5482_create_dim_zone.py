"""create_dim_zone

Revision ID: 7d3bd6bf5482
Revises: 5d39353d0e6b
Create Date: 2024-03-22 22:21:41.210821

"""

import sqlalchemy as sa
from alembic import op
from bloom.config import settings
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "7d3bd6bf5482"
down_revision = "5d39353d0e6b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dim_zone",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("category", sa.String, nullable=False),
        sa.Column("sub_category", sa.String),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("geometry", Geometry(geometry_type="GEOMETRY", srid=settings.srid)),
        sa.Column("centroid", Geometry(geometry_type="POINT", srid=settings.srid)),
        sa.Column("beneficiaries", sa.String),
        sa.Column("json_data", JSONB),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
    )
    op.create_index("i_dim_zone_created_updated", "dim_zone", ["created_at", "updated_at"])
    op.create_index("i_dim_zone_category", "dim_zone", ["category", "sub_category"])
    #op.add_column('dim_zone', sa.Column('beneficiaries', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_table("dim_zone")
