"""metrics add category

Revision ID: 2b9d9e61be30
Revises: c32d65d6e6fd
Create Date: 2024-12-11 12:33:19.307295

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2b9d9e61be30'
down_revision = 'c32d65d6e6fd'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('fct_metrics',sa.Column('zone_id',
                                            sa.Integer,
                                            sa.ForeignKey("dim_zone.id"),
                                            nullable=True))
    op.add_column('fct_metrics',sa.Column('zone_category',
                                            sa.String,
                                            nullable=True))
    op.execute("""
               update fct_metrics fm
               set zone_id = (select id
                              from dim_zone dz
                              where name = fm.zone_name and
                                    (sub_category = fm.zone_sub_category)),
               zone_category = (select category
                              from dim_zone dz
                              where name = fm.zone_name and
                              (sub_category = fm.zone_sub_category))
                where zone_id is null or zone_category is null""")
    pass


def downgrade() -> None:
    op.drop_column('fct_metrics','zone_category')
    op.drop_column('fct_metrics','zone_id')
    pass
