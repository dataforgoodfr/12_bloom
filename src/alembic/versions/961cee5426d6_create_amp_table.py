"""create amp table

Revision ID: 961cee5426d6
Revises: 1fd83d22bd1e
Create Date: 2024-02-11 22:10:19.010986

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector
import geoalchemy2

# revision identifiers, used by Alembic.
revision = '961cee5426d6'
down_revision = '1fd83d22bd1e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("mpa_fr_with_mn",
                    sa.Column("index", sa.Integer, primary_key=True),
                    sa.Column("wdpaid", sa.Integer),
                    sa.Column("name", sa.String, nullable=False),
                    sa.Column("desig_eng", sa.String),
                    sa.Column("desig_type", sa.String),
                    sa.Column("iucn_cat", sa.String),
                    sa.Column("parent_iso", sa.String),
                    sa.Column("iso3", sa.String),
                    sa.Column("geometry", geoalchemy2.types.Geometry(geometry_type="GEOMETRY",
                                          srid=4326)),
                    sa.Column("benificiaries", sa.String)
                    )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    sql_tables = inspector.get_table_names()
    tables = [
        "mpa_fr_with_mn",
    ]
    for t in tables:
        if t in sql_tables:
            op.drop_table(t)
