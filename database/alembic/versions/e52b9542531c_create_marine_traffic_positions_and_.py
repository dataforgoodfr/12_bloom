"""create marine traffic positions and polygons table

Revision ID: e52b9542531c
Revises: 
Create Date: 2023-03-31 17:05:34.275315

"""
import uuid

from alembic import op
import sqlalchemy as sa
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
from sqlalchemy import Inspector

revision = 'e52b9542531c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    downgrade()

    op.create_table(
        "marine_traffic_vessel_positions",
        sa.Column(
            "id", sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
        ),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("ship_name", sa.String),
        sa.Column("IMO", sa.String, index=True, nullable=False),
        sa.Column("vessel_id", sa.UUID, index=True, nullable=False, unique=True),
        sa.Column("mmsi", sa.String),
        sa.Column("last_position_time", sa.DateTime),
        sa.Column("fishing", sa.Boolean),
        sa.Column("at_port", sa.Boolean),
        sa.Column("port_name", sa.String),
        sa.Column("position", Geometry('POINT')),
        sa.Column("status", sa.String),
        sa.Column("speed", sa.Float),
        sa.Column("navigation_status", sa.String),
        keep_existing=False,
    )

    op.create_table(
        "spire_vessel_positions",
        sa.Column(
            "id", sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
        ),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("ship_name", sa.String),
        sa.Column("IMO", sa.String, index=True, nullable=False),
        sa.Column("vessel_id", sa.UUID, index=True, nullable=False, unique=True),
        sa.Column("mmsi", sa.String),
        sa.Column("last_position_time", sa.DateTime),
        sa.Column("fishing", sa.Boolean),
        sa.Column("at_port", sa.Boolean),
        sa.Column("port_name", sa.String),
        sa.Column("position", Geometry('POINT')),
        sa.Column("status", sa.String),
        sa.Column("speed", sa.Float),
        sa.Column("navigation_status", sa.String),
        keep_existing=False,
    )

    op.create_table(
        "vessels",
        sa.Column(
            "id", sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
        ),
        sa.Column("country_iso3", sa.String),
        sa.Column("cfr", sa.String),
        sa.Column("IMO", sa.String, index=True, nullable=False),
        sa.Column("registration_number", sa.String),
        sa.Column("external_marking", sa.String),
        sa.Column("ship_name", sa.String),
        sa.Column("ircs", sa.String),
        sa.Column("mmsi", sa.String),
        sa.Column("loa", sa.Float),
        sa.Column("type", sa.String),
        keep_existing=False,
    )

    op.create_foreign_key("fk_vessels_marine_traffic_vessel_positions", "vessels", "marine_traffic_vessel_positions", ["id"], ["vessel_id"])
    op.create_foreign_key("fk_vessels_spire_vessel_positions", "vessels", "spire_vessel_positions", ["id"], ["vessel_id"])

    op.create_table(
        "mpa",
        sa.Column(
            "id", sa.UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
        ),
        sa.Column("polygon", Geometry('POLYGON'), nullable=False),
        sa.Column("mpa_name", sa.String),
        sa.Column("mpa_strict", sa.Boolean),
        keep_existing=False,
    )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    sql_tables = inspector.get_table_names()
    tables = [
        "mpa",
        "vessels",
        "marine_traffic_vessel_positions",
        "spire_vessel_positions",
    ]
    for t in tables:
        if t in sql_tables:
            op.drop_table(t)

