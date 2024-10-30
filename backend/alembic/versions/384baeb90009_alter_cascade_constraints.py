"""alter_cascade_constraints

Revision ID: 384baeb90009
Revises: 06bb3c26076f
Create Date: 2024-10-30 13:16:54.442408

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '384baeb90009'
down_revision = '06bb3c26076f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("rel_segment_zone_segment_id_fkey", "rel_segment_zone")
    op.create_foreign_key("rel_segment_zone_segment_id_fkey", "rel_segment_zone", "fct_segment", ["segment_id"], ["id"], ondelete="CASCADE")
    op.drop_constraint("rel_segment_zone_zone_id_fkey", "rel_segment_zone")
    op.create_foreign_key("rel_segment_zone_zone_id_fkey", "rel_segment_zone", "dim_zone", ["zone_id"], ["id"], ondelete="CASCADE")
    op.drop_constraint("fct_segment_excursion_id_fkey", "fct_segment")
    op.create_foreign_key("fct_segment_excursion_id_fkey", "fct_segment", "fct_excursion", ["excursion_id"], ["id"], ondelete="CASCADE")

def downgrade() -> None:
    pass
