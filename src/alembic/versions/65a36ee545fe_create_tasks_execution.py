"""create_tasks_execution

Revision ID: 65a36ee545fe
Revises: 90bc2c589e44
Create Date: 2024-03-24 14:48:36.708906

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision = '65a36ee545fe'
down_revision = '90bc2c589e44'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table("tasks_executions",
                    sa.Column("task_name", sa.String, primary_key=True),
                    sa.Column("point_in_time", sa.DateTime(timezone=True)),
                    sa.Column(
                        "created_at",
                        sa.DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now(),
                    ),
                    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
                    )


def downgrade() -> None:
    op.drop_table("tasks_executions")
