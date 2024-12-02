"""add task execution 

Revision ID: d9d279892b5c
Revises: 7ba4634af5ad
Create Date: 2024-11-30 12:54:22.318425

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'd9d279892b5c'
down_revision = '7ba4634af5ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create a new task_executions table that permit to store historical data
    for each task execution
    The goal is to be able to detect timeframe not covered by Spire API interrogation
    """
    # drop constraint from existing table to free the constraint name
    op.drop_constraint(table_name="tasks_executions",
                       constraint_name="tasks_executions_pkey")
    # rename existing table to keep existing data
    op.rename_table('tasks_executions','tasks_executions_tmp')
    # create the new task_executions table with id and active columns in addition
    op.create_table("tasks_executions",
                    sa.Column("id", sa.Integer(),sa.Identity(), primary_key=True, index=True),
                    sa.Column("task_name", sa.String),
                    sa.Column("point_in_time", sa.DateTime(timezone=True)),
                    sa.Column(
                        "created_at",
                        sa.DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now(),
                    ),
                    sa.Column("updated_at", sa.DateTime(timezone=True), onupdate=func.now()),
                    sa.Column("delta",
                                sa.Interval,
                                index=True,
                                nullable=True),
                    sa.Column("active",
                                sa.Boolean,
                                index=True,
                                default=False),
                    )
    # copy of existing data to new table with active=True
    op.execute("insert into tasks_executions "
               +"(task_name,point_in_time,created_at,updated_at,active) "
               +"select task_name,point_in_time,created_at,updated_at,true "
               +"from tasks_executions_tmp")
    # drop old table
    op.drop_table('tasks_executions_tmp')
    pass


def downgrade() -> None:
    # delete all lines active=False as they have no equivalent in old task_executions
    op.execute("delete from tasks_executions where active=False")
    # drop active and id table
    op.drop_column("tasks_executions","active")
    op.drop_column("tasks_executions","id")
    # recreate the primary unique key constraint of old table
    op.create_unique_constraint("tasks_executions_pkey",
                                "tasks_executions",
                                ["task_name"],
                                )
    pass
