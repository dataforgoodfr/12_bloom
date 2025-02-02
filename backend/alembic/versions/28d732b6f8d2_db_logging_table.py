"""db logging table

Revision ID: 28d732b6f8d2
Revises: 5801cb8f1af5
Create Date: 2025-02-02 21:26:07.204234

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '28d732b6f8d2'
down_revision = '5801cb8f1af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("fct_logging",
                    sa.Column("id", sa.Integer, sa.Identity(), primary_key=True),
                    sa.Column(
                        "created_at",
                        sa.DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now(),
                    ),
                    sa.Column(
                        "timestamp",
                        sa.DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now(),
                    ),
                    sa.Column("level", sa.String, nullable=False,default="INFO"),
                    sa.Column("service", sa.String, nullable=False),
                    sa.Column("category", sa.String, nullable=True),
                    sa.Column("sub_category", sa.String, nullable=True),
                    sa.Column("json_data", JSONB,nullable=True,default=None),
                    )
    op.create_index("i_fct_logging_created", "fct_logging", ["created_at"])
    op.create_index("i_fct_logging_timestamp", "fct_logging", ["timestamp"])
    op.create_index("i_fct_logging", "fct_logging", ["category", "sub_category"])

def downgrade() -> None:
    op.drop_table("fct_logging")
