import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel
from sqlalchemy.orm import relationship
import logging

logger = logging.getLogger(__name__)


class ActorService(ProModel, ModelBase):
    """
    actor_service
    """
    __tablename__ = "actor_service"

    id = Column(Integer, Sequence("actor_service_id_seq", start=100000), primary_key=True)  # actor_service id
    actor_id = Column(Integer, ForeignKey("actor.id"))  # 用户id
    service_id = Column(Integer, ForeignKey("service.id"))  # 服务id
    service_name = Column(String, nullable=False)  # 服务名称
    last_buy_time = Column(DateTime, nullable=False, default=datetime.datetime.now)  # 最近购买时间
    package_time = Column(Integer, nullable=False, default=0)  # 套餐余量
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期

    service = relationship("Service")  # 对应服务
    actor = relationship("Actor", back_populates="services")  # 对应服务

    @classmethod
    async def get_my_service(cls, session, actor_id, service_id):
        return session.query(cls).filter(cls.actor_id == actor_id, cls.service_id == service_id).one_or_none()

    @classmethod
    async def get_member_services(cls, session, actor_id):
        return session.query(cls).filter(cls.actor_id == actor_id).all()

    @classmethod
    async def get_service_by_type(cls, session, actor_id, service_type):
        return session.query(cls).join(Service, isouter=True).filter(cls.actor_id == actor_id,
                                                                     Service.service_type == service_type).one_or_none()

    @classmethod
    async def deduct_package_time(cls, session, actor_id, service_id, times):
        actor_service = session.query(cls).filter(cls.actor_id == actor_id, cls.service_id == service_id).one_or_none()
        if not actor_service:
            logger.error("deduct package_time failed，Service not exists！")
            return False
        if actor_service.package_time < times:
            logger.error("deduct package_time failed，times not enough！")
            return False
        actor_service.package_time = actor_service.package_time - times
        session.commit()


class Service(ProModel, ModelBase):
    """
    Service
    """
    __tablename__ = "service"

    id = Column(Integer, Sequence("service_id_seq", start=100000), primary_key=True)  # service id
    service_name = Column(String, nullable=False)  # 服务名称
    sub_heading = Column(String, nullable=True)  # 副标题
    service_picture = Column(String, nullable=True)  # 服务图片
    price = Column(Float, nullable=False)  # 单价，如0.005/次
    remark = Column(String, nullable=True)  # 备注
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期
    enable = Column(Boolean, default=true)  # 是否可用
    instruction = Column(String, nullable=True)  # 服务说明，html
    order_no = Column(Integer, default=0)  # 排序号,越大越往前排
    category_id = Column(Integer, ForeignKey("category.id"))  # 所属分类
    delete_flag = Column(Boolean, default=False)  # 删除标志
    service_type = Column(Integer, nullable=False)  # 服务类型

    packages = relationship("Package", order_by="Package.order_no.desc()",
                            back_populates="service",
                            uselist=true)  # 拥有的套餐
    category = relationship("Category", back_populates="services")  # 所属分类

    def to_json(self):
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if key == "created_time":
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            result[key] = value

        return result

    @classmethod
    async def get(cls, session, pk):
        return session.query(cls).get(pk)

    @classmethod
    async def get_all(cls, session, enable=True, delete_flag=False):
        if enable is not None:
            return session.query(cls).filter(cls.enable == enable, cls.delete_flag == delete_flag).order_by(
                desc(cls.order_no)).all()
        return session.query(cls).all()

    @classmethod
    async def query(cls, session, name=None, offset: int = None, limit: int = None):
        query = session.query(cls)
        total = query.count()
        data = []
        if total:
            if name:
                query = query.filter(cls.service_name.like(f'%{name}%'))
            query = query.filter(cls.delete_flag == False)
            query = query.order_by(desc(cls.order_no))
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            data = query.all()
        return data, total


class Package(ProModel, ModelBase):
    """
    Package
    """
    __tablename__ = "package"

    id = Column(Integer, Sequence("package_id_seq", start=100000), primary_key=True)  # package id
    package_name = Column(String, nullable=False)  # 套餐名称，如首次使用套餐
    package_price = Column(Float, nullable=False)  # 套餐价格
    times = Column(Integer, nullable=False)  # 可使用次数
    remark = Column(String, nullable=True)  # 备注
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期
    service_id = Column(Integer, ForeignKey('service.id'))
    can_buy_again = Column(Boolean, default=true)  # 是否可重复购买
    is_marked_price = Column(Boolean, default=False)  # 是否标价
    enable = Column(Boolean, default=true)  # 是否可用
    package_type = Column(Integer, default=1)  # 套餐类型，1：免费，2：收费
    order_no = Column(Integer, default=0)  # 排序
    delete_flag = Column(Boolean, default=False)  # 删除标志

    service = relationship("Service", back_populates="packages")  # 所属服务

    def to_json(self):
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            result[key] = value
        return result

    @classmethod
    async def get(cls, session, pk):
        return session.query(cls).get(pk)

    @classmethod
    async def get_service_marked_price(cls, session, service_id):
        return session.query(cls).filter(cls.service_id == service_id, cls.enable == True,
                                         cls.is_marked_price == True).order_by(desc(cls.order_no)).limit(
            1).one_or_none()


class ServicePackageBuyingLog(ProModel, ModelBase):
    """
    服务套餐购买记录
    """
    __tablename__ = "service_package_buying_log"

    id = Column(Integer, Sequence("service_package_buying_log_id_seq", start=100000),
                primary_key=True)  # service_package_buying_log id
    actor_id = Column(Integer, ForeignKey("actor.id"))  # 用户id
    service_id = Column(Integer, ForeignKey("service.id"))  # 服务id
    package_id = Column(Integer, ForeignKey("package.id"))  # 套餐id
    payment_price = Column(Float, nullable=False)  # 实际支付金额
    service_order_id = Column(Integer)  # 订单id
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期

    @classmethod
    async def check_can_buy_again(cls, session, actor_id, package_id):
        return session.query(cls).filter(cls.actor_id == actor_id, cls.package_id == package_id).one_or_none()


class ServiceConsumeLog(ProModel, ModelBase):
    """
    服务套餐购买记录
    """
    __tablename__ = "service_consume_log"

    id = Column(Integer, Sequence("service_consume_log_id_seq", start=100000),
                primary_key=True)  # service_consume_log id
    actor_id = Column(Integer, ForeignKey("actor.id"))  # 用户id
    service_id = Column(Integer, ForeignKey("service.id"))  # 服务id
    consume_times = Column(Integer, nullable=False)  # 消费次数
    before_consume_times = Column(Integer, nullable=False)  # 消费前次数
    after_consume_times = Column(Integer, nullable=False)  # 消费后次数
    consume_reason = Column(String)  # 消费原因
    task_id = Column(Integer, ForeignKey("task.id"))  # 任务id
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建日期

    def to_json(self):
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if key == "created_time":
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            result[key] = value
        return result

    @classmethod
    async def log(cls, session, actor_id, service_id, times, before_times, after_times, reason, task_id):
        log = cls()
        log.actor_id = actor_id
        log.service_id = service_id
        log.consume_times = times
        log.before_consume_times = before_times
        log.after_consume_times = after_times
        log.consume_reason = reason
        log.task_id = task_id
        session.add(log)
        session.commit()

    @classmethod
    async def query(cls, session, actor_id, service_id, offset, limit):
        q = session.query(cls).filter(cls.actor_id == actor_id, cls.service_id == service_id)
        total = q.count()
        if total:
            q = q.order_by(desc(cls.created_time))
            if offset:
                q = q.offset(offset)
            if limit:
                q = q.limit(limit)
        return total, q.all()
