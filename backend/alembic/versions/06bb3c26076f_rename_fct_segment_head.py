"""rename_fct_segment_head

Revision ID: 06bb3c26076f
Revises: 31227ff28c79
Create Date: 2024-05-18 21:13:00.622006

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '06bb3c26076f'
down_revision = '31227ff28c79'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("fct_segment", "heading", new_column_name="course")


def downgrade() -> None:
    op.alter_column("fct_segment", "course", new_column_name="heading")
