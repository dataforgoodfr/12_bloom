"""create dim_port table

Revision ID: 7962eee40abe
Revises: 961cee5426d6
Create Date: 2024-02-26 18:38:37.726130

"""
import sqlalchemy as sa
from geoalchemy2 import Geometry

from alembic import op

# revision identifiers, used by Alembic.
revision = "7962eee40abe"
down_revision = "6734d9afbba5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    dim_port.csv contains data for ports
    """
    op.create_table(
        "dim_port",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("port_name", sa.String(255), nullable=False),
        sa.Column("locode", sa.String(255), nullable=False),
        sa.Column("url", sa.String(255), nullable=False),
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
        sa.Column("latitude", sa.String(255), nullable=False),
        sa.Column("longitude", sa.String(255), nullable=False),
        sa.Column("country-iso3", sa.String(3), nullable=False),
        sa.Column("country_name", sa.String(255), nullable=False),
        sa.Column("has_excursion", sa.Boolean, nullable=True),
        sa.Column("created_at", sa.TIMESTAMP, nullable=True),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=True),
    )



def downgrade() -> None:
    op.drop_table("dim_port")
