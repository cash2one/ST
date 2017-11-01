import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel
from sqlalchemy.orm import relationship


class Category(ProModel, ModelBase):
    """
    category
    """
    __tablename__ = "category"

    id = Column(Integer, Sequence("category_id_seq", start=100000), primary_key=True)  # category id
    category_name = Column(String, nullable=False)  # 分类名称
    enable = Column(Boolean, default=true)  # 是否可用
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期

    services = relationship("Service", back_populates="category", uselist=true)

    def to_json(self):
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            result[key] = value
        return result

    @classmethod
    async def get_all(cls, session, enable=None):
        query = session.query(cls)
        if enable:
            query = query.filter(cls.enable == enable)
        return query.all()
