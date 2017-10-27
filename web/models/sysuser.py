import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel


class SysUser(ProModel, ModelBase):
    """
    sys_user
    """
    __tablename__ = "sys_user"

    id = Column(Integer, Sequence("sys_user_seq", start=100000), primary_key=True)  # sys_user id
    username = Column(String, nullable=False)  # 用户名
    password = Column(String, nullable=False)

    is_locked = Column(Boolean, default=False)
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期

    @classmethod
    async def get(cls, session, pk):
        return session.query(cls).get(pk)

    @classmethod
    async def get_by_username(cls, session, username):
        actor = session.query(cls).filter(cls.username == username).one_or_none()
        return actor

    def to_json(self):
        return {"id": self.id, "username": self.username, "is_locked": self.is_locked}
