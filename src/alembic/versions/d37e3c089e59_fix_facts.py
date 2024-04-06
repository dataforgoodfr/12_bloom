"""fix_facts

Revision ID: d37e3c089e59
Revises: 4e912be8a176
Create Date: 2024-04-06 10:03:51.978288

"""
from alembic import op
import sqlalchemy as sa
from bloom.config import settings
from geoalchemy2 import Geometry

# revision identifiers, used by Alembic.
revision = 'd37e3c089e59'
down_revision = '4e912be8a176'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("fct_segment", "start_position_id")
    op.drop_column("fct_segment", "end_position_id")
    op.add_column("fct_segment", sa.Column("start_position", Geometry(geometry_type="POINT", srid=settings.srid)))
    op.add_column("fct_segment", sa.Column("end_position", Geometry(geometry_type="POINT", srid=settings.srid)))
    op.add_column("fct_segment", sa.Column("speed_at_start", sa.Float))
    op.add_column("fct_segment", sa.Column("speed_at_end", sa.Float))

    op.drop_column("fct_excursion", "departure_position_id")
    op.drop_column("fct_excursion", "arrival_position_id")
    op.add_column("fct_excursion", sa.Column("departure_position", Geometry(geometry_type="POINT", srid=settings.srid)))
    op.add_column("fct_excursion", sa.Column("arrival_position", Geometry(geometry_type="POINT", srid=settings.srid)))


def downgrade() -> None:
    op.drop_column("fct_segment", "start_position")
    op.drop_column("fct_segment", "end_position")
    op.drop_column("fct_segment", "speed_at_start")
    op.drop_column("fct_segment", "speed_at_end")
    op.add_column("fct_segment", sa.Column("start_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")))
    op.add_column("fct_segment", sa.Column("end_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")))

    op.drop_column("fct_excursion", "departure_position")
    op.drop_column("fct_excursion", "arrival_position")
    op.add_column("fct_excursion", sa.Column("departure_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")))
    op.add_column("fct_excursion", sa.Column("arrival_position_id", sa.Integer, sa.ForeignKey("vessel_positions.id")))
