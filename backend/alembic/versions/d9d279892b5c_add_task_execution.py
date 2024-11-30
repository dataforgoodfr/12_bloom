"""add task execution 

Revision ID: d9d279892b5c
Revises: 7ba4634af5ad
Create Date: 2024-11-30 12:54:22.318425

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd9d279892b5c'
down_revision = '7ba4634af5ad'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("delete from tasks_executions")
    op.drop_constraint(table_name="tasks_executions",
                       constraint_name="tasks_executions_pkey")
    op.add_column(  "tasks_executions",
                    sa.Column("id",
                    sa.Integer, 
                    sa.Identity(),
                    primary_key=True,
                    index=True,))
    op.create_primary_key("tasks_executions_pkey",
                          "tasks_executions",
                          ["id"])
    #op.add_column(  "tasks_executions",
    #                sa.Column("id",
    #                sa.Integer, 
    #                sa.Identity(),
    #                primary_key=True,
    #                index=True,))
    op.add_column(  "tasks_executions",
                    sa.Column(
                    "active",
                    sa.Boolean,
                    index=True,
                    default=False))
    pass


def downgrade() -> None:
    op.drop_column("tasks_executions","active")
    op.drop_column("tasks_executions","id")
    op.create_unique_constraint("tasks_executions_pkey",
                                "tasks_executions",
                                ["task_name"],
                                )
    pass
