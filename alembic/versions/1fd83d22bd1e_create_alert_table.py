"""create alert table

Revision ID: 1fd83d22bd1e
Revises: e52b9542531c
Create Date: 2023-06-26 23:06:06.323214

"""
import uuid

import sqlalchemy as sa
from sqlalchemy import Inspector

from alembic import op

# revision identifiers, used by Alembic.
revision = "1fd83d22bd1e"
down_revision = "e52b9542531c"
branch_labels = None
depends_on = None


def upgrade() -> None:

    op.create_table(
        "alert",
        sa.Column(
            "id",
            sa.Integer,
            sa.Identity(),
            primary_key=True,
            index=True,
            default=uuid.uuid4,
        ),
        sa.Column("timestamp", sa.DateTime),
        sa.Column("vessel_id", sa.Integer, index=True, nullable=False),
        sa.Column("mpa_id", sa.Integer, index=True, nullable=False),
        keep_existing=False,
    )

    op.create_foreign_key(
        "fk_alert_vessels",
        "alert",
        "vessels",
        ["vessel_id"],
        ["id"],
    )

    op.create_foreign_key(
        "fk_alert_mpa",
        "alert",
        "mpa",
        ["mpa_id"],
        ["index"],
    )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    sql_tables = inspector.get_table_names()
    tables = [
        "alert",
    ]
    for t in tables:
        if t in sql_tables:
            op.drop_table(t)
