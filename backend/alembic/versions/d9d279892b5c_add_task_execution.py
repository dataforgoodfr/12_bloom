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
    op.drop_constraint(table_name="tasks_executions",
                       constraint_name="tasks_executions_pkey")
    op.rename_table('tasks_executions','tasks_executions_tmp')
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
                    sa.Column("active",
                                sa.Boolean,
                                index=True,
                                default=False),
                    )
    op.execute("insert into tasks_executions "
               +"(task_name,point_in_time,created_at,updated_at,active) "
               +"select task_name,point_in_time,created_at,updated_at,true "
               +"from tasks_executions_tmp")
    #conn=op.get_bind()
    #query=conn.execute("select task_name,point_in_time,created_at,updated_at from tasks_executions_tmp")
    #results = query.fetchall()
    #executions=[{'task_name': row[0],
    #             'point_in_time': row[1],
    #             'created_at': row[2],
    #             'updated_at': row[3]} for row in results]
    #op.bulk_insert('tasks_executions',executions)
    op.drop_table('tasks_executions_tmp')
    pass


def downgrade() -> None:
    op.execute("delete from tasks_executions where active=False")
    op.drop_column("tasks_executions","active")
    op.drop_column("tasks_executions","id")
    op.create_unique_constraint("tasks_executions_pkey",
                                "tasks_executions",
                                ["task_name"],
                                )
    pass
