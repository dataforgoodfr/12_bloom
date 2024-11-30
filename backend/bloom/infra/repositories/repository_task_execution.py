from datetime import datetime, timezone

from bloom.infra.database import sql_model
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import update
from sqlalchemy.orm import Session


class TaskExecutionRepository:
    @staticmethod
    def get_point_in_time(session: Session, task_name: str) -> datetime:
        stmt = select(sql_model.TaskExecution)\
                .where(sql_model.TaskExecution.task_name == task_name)\
                .where(sql_model.TaskExecution.active == True)
        e = session.execute(stmt).scalar()
        if not e:
            return datetime.fromtimestamp(0, timezone.utc)
        else:
            return e.point_in_time

    def set_point_in_time(session: Session, task_name: str, pit: datetime) -> None:
        stmt= ( update(sql_model.TaskExecution)
                .where(sql_model.TaskExecution.task_name==task_name)
                .where(sql_model.TaskExecution.active==True)
                .values(active=False)
            )
        session.execute(stmt)
        stmt = insert(sql_model.TaskExecution).values(
                    task_name=task_name,
                    point_in_time=pit,
                    active=True)
        session.execute(stmt)
