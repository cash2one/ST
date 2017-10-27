import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel
from sqlalchemy.orm import relationship


class Task(ProModel, ModelBase):
    """
    Task
    """
    __tablename__ = "task"

    id = Column(Integer, Sequence("task_id_seq", start=100000), primary_key=True)  # task id
