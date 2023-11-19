"""add columns in spire table

Revision ID: 68c9f220a07f
Revises: 1fd83d22bd1e
Create Date: 2023-07-07 11:15:16.516122

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "68c9f220a07f"
down_revision = "e52b9542531c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("spire_vessel_positions") as batch_op:
        batch_op.add_column(sa.Column("vessel_length", sa.Integer))
        batch_op.add_column(sa.Column("vessel_width", sa.Integer))
        batch_op.add_column(sa.Column("voyage_destination", sa.String))
        batch_op.add_column(sa.Column("voyage_draught", sa.Float))
        batch_op.add_column(sa.Column("voyage_eta", sa.DateTime))
        batch_op.add_column(sa.Column("accuracy", sa.String))
        batch_op.add_column(sa.Column("position_sensors", sa.String))
        batch_op.add_column(sa.Column("course", sa.Float))
        batch_op.add_column(sa.Column("heading", sa.Float))
        batch_op.add_column(sa.Column("rot", sa.Float))
        batch_op.drop_column("fishing")
        batch_op.drop_column("at_port")
        batch_op.drop_column("port_name")
        batch_op.drop_column("status")


def downgrade() -> None:
    with op.batch_alter_table("spire_vessel_positions") as batch_op:
        batch_op.drop_column("vessel_length")
        batch_op.drop_column("vessel_width")
        batch_op.drop_column("voyage_destination")
        batch_op.drop_column("voyage_draught")
        batch_op.drop_column("voyage_eta")
        batch_op.drop_column("accuracy")
        batch_op.drop_column("position_sensors")
        batch_op.drop_column("course")
        batch_op.drop_column("heading")
        batch_op.drop_column("rot")
        batch_op.add_column(sa.Column("fishing", sa.Boolean))
        batch_op.add_column(sa.Column("at_port", sa.Boolean))
        batch_op.add_column(sa.Column("port_name", sa.String))
        batch_op.add_column(sa.Column("status", sa.String))
