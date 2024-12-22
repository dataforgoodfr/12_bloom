"""task_execution_add_duration_position

Revision ID: 2e4561a69da9
Revises: 5801cb8f1af5
Create Date: 2024-12-21 22:04:04.659923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '2e4561a69da9'
down_revision = '5801cb8f1af5'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('tasks_executions',sa.Column("duration",
                                sa.Interval,
                                nullable=True))
    op.add_column('tasks_executions',sa.Column("position_count",
                                sa.Integer,
                                nullable=True))
    pass


def downgrade() -> None:
    op.drop_column('tasks_executions',"position_count")
    op.drop_column('tasks_executions',"duration")
    pass
