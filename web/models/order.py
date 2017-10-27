import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel
from sqlalchemy.orm import relationship
from .actor import Actor


class ServiceOrder(ProModel, ModelBase):
    """
    服务订单
    """
    __tablename__ = "service_order"

    id = Column(Integer, Sequence("service_order_id_seq", start=100000), primary_key=True)  # service_order id
    actor_id = Column(Integer, ForeignKey("actor.id"))  # 用户id
    service_id = Column(Integer, ForeignKey("service.id"))  # 服务id
    package_id = Column(Integer, ForeignKey("package.id"))  # 套餐id
    payment_price = Column(Float, nullable=false, default=0)  # 实际支付金额
    payment_time = Column(DateTime)  # 支付时间
    payment_type = Column(Integer)  # 支付方式
    order_status = Column(Integer, default=1)  # 订单状态 1：已确认，2：已取消，3：已退货
    payment_status = Column(Integer, default=1)  # 支付状态 1：未支付，2：已支付，3：已退款
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期

    service = relationship("Service")
    package = relationship("Package")
    actor = relationship("Actor")

    @classmethod
    async def query(cls, session, phone=None, offset: int = None, limit: int = None):
        query = session.query(cls)
        total = query.count()
        data = []
        if total:
            if phone:
                query = query.join(Actor, isouter=True).filter(Actor.phone == phone)
            query = query.order_by(desc(cls.created_time))
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            data = query.all()
        return data, total

    @classmethod
    async def get(cls, session, pk):
        return session.query(cls).get(pk)
