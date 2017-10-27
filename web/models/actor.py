import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel
from sqlalchemy.orm import relationship


class Actor(ProModel, ModelBase):
    """
    Actor
    """
    __tablename__ = "actor"

    id = Column(Integer, Sequence("actor_id_seq", start=100000), primary_key=True)  # actor id
    phone = Column(String, nullable=False)  # 手机号（用户名）
    password = Column(String, nullable=False)

    is_locked = Column(Boolean, default=False)
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期

    services = relationship("ActorService", back_populates="actor", uselist=true)  # 拥有的的服务

    @classmethod
    async def get(cls, session, pk):
        return session.query(cls).get(pk)

    @classmethod
    async def get_by_phone(cls, session, phone):
        actor = session.query(cls).filter(cls.phone == phone).one_or_none()
        return actor

    def to_json(self):
        return {"id": self.id, "username": self.phone, "is_locked": self.is_locked,
                "created_time": self.created_time.strftime('%Y-%m-%d %H:%M:%S')}

    @classmethod
    async def query(cls, session, phone=None, offset: int = None, limit: int = None):
        query = session.query(cls)
        total = query.count()
        data = []
        if total:
            if phone:
                query = query.filter(cls.phone == phone)
            query = query.order_by(desc(cls.created_time))
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            data = query.all()
        return data, total
