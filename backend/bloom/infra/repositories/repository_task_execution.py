from datetime import datetime, timezone, timedelta

from bloom.infra.database import sql_model
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.expression import update,asc,desc,delete
from sqlalchemy.orm import Session


class TaskExecutionRepository:
    @staticmethod
    def get_point_in_time(session: Session, task_name: str) -> datetime:
        stmt = select(sql_model.TaskExecution)\
                .where(sql_model.TaskExecution.task_name == task_name)\
                .where(sql_model.TaskExecution.active == True)
        e = session.execute(stmt).scalar_one_or_none()
        if not e:
            return datetime.fromtimestamp(0, timezone.utc)
        else:
            return e.point_in_time
        
    def set_duration(session: Session, task_name: str, pit: datetime,duration:timedelta)->None:
        stmt = (update(sql_model.TaskExecution)
                .where(sql_model.TaskExecution.task_name==task_name)
                .where(sql_model.TaskExecution.point_in_time==pit)
                .values(duration=duration)
        )
        session.execute(stmt)
    def set_position_count(session: Session, task_name: str, pit: datetime,count:int)->None:
        stmt = (update(sql_model.TaskExecution)
                .where(sql_model.TaskExecution.task_name==task_name)
                .where(sql_model.TaskExecution.point_in_time==pit)
                .values(position_count=count)
        )
        session.execute(stmt)


    def set_point_in_time(session: Session, task_name: str, pit: datetime) -> None:
        stmt= ( update(sql_model.TaskExecution)
                .where(sql_model.TaskExecution.task_name==task_name)
                .values(active=False)
            )
        session.execute(stmt)
        subquery_delta=select(pit-sql_model.TaskExecution.point_in_time)\
                        .select_from(sql_model.TaskExecution)\
                        .where(sql_model.TaskExecution.task_name==task_name)\
                        .order_by(desc(sql_model.TaskExecution.point_in_time))\
                        .limit(1).subquery()
        stmt = insert(sql_model.TaskExecution).values(
                    task_name=task_name,
                    point_in_time=pit,
                    delta=subquery_delta,
                    active=True)
        session.execute(stmt)
    
    def remove_point_in_time(session: Session, task_name: str, pit: datetime) -> None:
        stmt= (delete(sql_model.TaskExecution)
               .where(sql_model.TaskExecution.task_name==task_name)
               .where(sql_model.TaskExecution.point_in_time==pit)
               )
        session.execute(stmt)
        subquery_last_pit=select(sql_model.TaskExecution.point_in_time)\
                        .select_from(sql_model.TaskExecution)\
                        .where(sql_model.TaskExecution.task_name==task_name)\
                        .order_by(desc(sql_model.TaskExecution.point_in_time))\
                        .limit(1).subquery()
        stmt = (update(sql_model.TaskExecution)
                .where(sql_model.TaskExecution.task_name==task_name)
                .where(sql_model.TaskExecution.point_in_time==subquery_last_pit)
                .values(active=True)
                )
        session.execute(stmt)
