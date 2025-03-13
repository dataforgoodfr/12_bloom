"""SCD implementation for dim_vessel/dim_zone

Revision ID: c02d2b79eab2
Revises: 5801cb8f1af5
Create Date: 2025-03-13 21:04:11.148024

"""
from alembic import op
import sqlalchemy as sa
from bloom.config import settings


# revision identifiers, used by Alembic.
revision = 'c02d2b79eab2'
down_revision = '5801cb8f1af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create SCD columns for dim_vessel and dim_zone with existing data (nullable)
    op.add_column("dim_vessel",sa.Column("scd_start",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_vessel",sa.Column("scd_end",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_vessel",sa.Column("scd_active",sa.Boolean,nullable=True))
    op.add_column("dim_vessel",sa.Column("uuid",sa.String,nullable=True))
    
    op.add_column("dim_zone",sa.Column("scd_start",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_zone",sa.Column("scd_end",sa.DateTime(timezone=True),nullable=True))
    op.add_column("dim_zone",sa.Column("scd_active",sa.Boolean,nullable=True))
    op.add_column("dim_zone",sa.Column("uuid",sa.String,nullable=True))

    # Initialize scd_column values
    op.execute( (f"update dim_vessel set scd_start = '{settings.scd_past_limit.isoformat()}',"
                 f"scd_end = '{settings.scd_future_limit.isoformat()}',"
                 f"scd_active = true,"
                 f"uuid = (CASE WHEN imo IS NOT NULL THEN imo::varchar(255) ELSE cfr END)"
                 ))
    
    op.execute( (f"update dim_zone set scd_start = '{settings.scd_past_limit.isoformat()}',"
                 f"scd_end = '{settings.scd_future_limit.isoformat()}',"
                 f"scd_active = true,"
                 f"uuid = COALESCE(category,'')||'/'||COALESCE(sub_category,'')||'/'||name"
                 ))
    
    # Set scd columns not nullable after init
    op.alter_column("dim_vessel","scd_start",nullable=False)
    op.alter_column("dim_vessel","scd_end",nullable=False)
    op.alter_column("dim_vessel","scd_active",nullable=False)
    op.alter_column("dim_vessel","uuid",nullable=False)
    
    op.alter_column("dim_zone","scd_start",nullable=False)
    op.alter_column("dim_zone","scd_end",nullable=False)
    op.alter_column("dim_zone","scd_active",nullable=False)
    op.alter_column("dim_zone","uuid",nullable=False)
    pass


def downgrade() -> None:
    op.drop_column("dim_zone","scd_start")
    op.drop_column("dim_zone","scd_end")
    op.drop_column("dim_zone","scd_active")
    op.drop_column("dim_zone","uuid")

    op.drop_column("dim_vessel","scd_start")
    op.drop_column("dim_vessel","scd_end")
    op.drop_column("dim_vessel","scd_active")
    op.drop_column("dim_vessel","uuid")
    pass
