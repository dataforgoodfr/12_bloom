"""Clean position on updated vessels only

Revision ID: dbe1b900df12
Revises: 5bfe00a08853
Create Date: 2024-12-26 13:10:19.501996

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dbe1b900df12'
down_revision = '5bfe00a08853'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("spire_ais_data",
                    "spire_ais_data_spire_update_statement_idx",
                    ["spire_update_statement"])
    pass


def downgrade() -> None:
    op.drop_index("spire_ais_data",
                  "spire_ais_data_spire_update_statement_idx")
    pass
