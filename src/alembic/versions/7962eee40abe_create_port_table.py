"""create ports table

Revision ID: 7962eee40abe
Revises: 961cee5426d6
Create Date: 2024-02-26 18:38:37.726130

"""

import sqlalchemy as sa
from alembic import op
from bloom.config import settings
from geoalchemy2 import Geometry
from sqlalchemy import Inspector
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = "7962eee40abe"
down_revision = "6734d9afbba5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    ports.csv contains data for ports
    url;country;port;locode;latitude;longitude;geometry_point;geometry_buffer
    https://www.vesselfinder.com/ports/ALSAR001;Albania;Sarande;ALSAR;39.8701;20.0062;POINT(20.0062 39.8701 # noqa E501
    """
    op.create_table(
        "dim_port",
        sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("locode", sa.String, nullable=False, unique=True),
        sa.Column("url", sa.String, nullable=False),
        sa.Column("country_iso3", sa.String, nullable=False),
        sa.Column("latitude", sa.Double, nullable=False),
        sa.Column("longitude", sa.Double, nullable=False),
        sa.Column(
            "geometry_point",
            Geometry(geometry_type="POINT", srid=settings.srid),
            nullable=False,
        ),
        sa.Column(
            "geometry_buffer",
            Geometry(geometry_type="POLYGON", srid=settings.srid),
        ),
        sa.Column("has_excursion", sa.Boolean, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
    )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    sql_tables = inspector.get_table_names()
    tables = ["dim_port", "ports"]
    for t in tables:
        if t in sql_tables:
            op.drop_table(t)
