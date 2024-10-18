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
down_revision = '06bb3c26076f'
branch_labels = None
depends_on = None


def upgrade() -> None:

    # Création de la table fct_metrics
    op.create_table(
        'fct_metrics',
        sa.Column('timestamp', sa.DateTime, primary_key=True), #granule
        sa.Column('vessel_id', sa.Integer, nullable=False), #vessel id
        sa.Column('type', sa.String, nullable=False), #in_mpa or at_sea
        sa.Column('duration_total', sa.DateTime, nullable=False), #time spent at sea at timestamp
        sa.Column('duration_fishing', sa.DateTime, nullable=True), #time spent fishing 
        sa.Column("mpa_name", sa.String, nullable=True), # if type is in_mpa, write here the mpa name
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