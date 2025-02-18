"""create fct metrics

Revision ID: c32d65d6e6fd
Revises: 06bb3c26076f
Create Date: 2024-10-18 11:13:02.468934

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import Inspector
import geoalchemy2

# revision identifiers, used by Alembic.
revision = 'c32d65d6e6fd'
down_revision = 'd9d279892b5c'
branch_labels = None
depends_on = None


def upgrade() -> None:

    # Création de la table fct_metrics
    op.create_table(
        'fct_metrics',
        sa.Column('timestamp', sa.DateTime, primary_key=True),
        sa.Column('vessel_id', sa.Integer, primary_key=True),
        sa.Column('type', sa.String, nullable=False), 
        sa.Column('vessel_mmsi', sa.Integer, nullable=False),
        sa.Column('ship_name', sa.String, nullable=False),
        sa.Column('vessel_country_iso3', sa.String, nullable=False),
        sa.Column('vessel_imo', sa.Integer),
        sa.Column('duration_total', sa.Interval, nullable=False),
        sa.Column('duration_fishing', sa.Interval, nullable=True),
        sa.Column("zone_name", sa.String, primary_key=True),
        sa.Column('zone_sub_category', sa.String, nullable=True),
    )


def downgrade() -> None:
    # Suppression de la table fct_metrics en cas de rollback
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    sql_tables = inspector.get_table_names()
    tables = [
        "fct_metrics",
    ]
    for t in tables:
        if t in sql_tables:
            op.drop_table(t)
            
