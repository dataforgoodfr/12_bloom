from bloom.infra.database import sql_model
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert


class TaskExecutionRepository:
    @staticmethod
    def get_point_in_time(session: Session, task_name: str) -> datetime:
        stmt = select(sql_model.TaskExecution).where(sql_model.TaskExecution.task_name == task_name)
        e = session.execute(stmt).scalar()
        if not e:
            return None
        else:
            return e.point_in_time

    def set_point_in_time(session: Session, task_name: str, pit: datetime) -> None:
        stmt = insert(sql_model.TaskExecution).values(task_name=task_name, point_in_time=pit).on_conflict_do_update(
            index_elements=["task_name"], set_=dict(point_in_time=pit, updated_at=datetime.now(timezone.utc)))
        session.execute(stmt)
