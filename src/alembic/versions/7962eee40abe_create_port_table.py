"""create ports table

Revision ID: 7962eee40abe
Revises: 961cee5426d6
Create Date: 2024-02-26 18:38:37.726130

"""
import sqlalchemy as sa
from geoalchemy2 import Geometry

from alembic import op

# revision identifiers, used by Alembic.
revision = "7962eee40abe"
down_revision = "961cee5426d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    ports.csv contains data for ports
    url;country;port;locode;latitude;longitude;geometry_point;geometry_buffer
    https://www.vesselfinder.com/ports/ALSAR001;Albania;Sarande;ALSAR;39.8701;20.0062;POINT (20.0062 39.8701
    """
    op.create_table(
        "ports",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("country", sa.String(255), nullable=False),
        sa.Column("port", sa.String(255), nullable=False),
        sa.Column("url", sa.String(255), nullable=False),
        sa.Column("locode", sa.String(255), nullable=False),
        sa.Column("latitude", sa.String(255), nullable=False),
        sa.Column("longitude", sa.String(255), nullable=False),
        sa.Column(
            "geometry_point",
            Geometry(geometry_type="POINT", srid=4326),
            nullable=False,
        ),
        sa.Column(
            "geometry_buffer",
            Geometry(geometry_type="POLYGON", srid=4326),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("ports")
