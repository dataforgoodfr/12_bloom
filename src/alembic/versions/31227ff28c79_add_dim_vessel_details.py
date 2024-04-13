"""add_dim_vessel_details

Revision ID: 31227ff28c79
Revises: d37e3c089e59
Create Date: 2024-04-10 21:05:07.204612

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '31227ff28c79'
down_revision = 'd37e3c089e59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("dim_vessel", sa.Column("details", sa.String))
    op.add_column("dim_vessel", sa.Column("length_class", sa.String))
    op.add_column("dim_vessel", sa.Column("check", sa.String))

    op.drop_column("dim_vessel", "registration_number")


def downgrade() -> None:
    op.add_column("dim_vessel", sa.Column("registration_number", sa.String))
    op.drop_column("dim_vessel", "details")
    op.drop_column("dim_vessel", "length_class")
    op.drop_column("dim_vessel", "check")
