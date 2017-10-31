import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel
from web.core import constants
from sqlalchemy.orm import relationship


class Task(ProModel, ModelBase):
    """
    Task
    """
    __tablename__ = "task"

    id = Column(Integer, Sequence("task_id_seq", start=100000), primary_key=True)  # task id
    actor_id = Column(Integer, ForeignKey("actor.id"))  # 用户id
    task_name = Column(String, nullable=false)  # 任务名称
    task_status = Column(Integer, nullable=false, default=constants.TASK_STATUS_INIT)
    task_result = Column(JSON, nullable=true)  # 执行结果
    service_id = Column(Integer, ForeignKey("service.id"))  # 所属服务
    service_type = Column(Integer, nullable=false)  # 服务类型，10000：BaiduPcTop50
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建时间
    delete_flag = Column(Boolean, default=false)  # 删除标志

    service = relationship("Service")

    def to_json(self):
        result = {}
        for key, value in self.__dict__.items():
            if key.startswith('_'):
                continue
            if key == "created_time":
                value = value.strftime('%Y-%m-%d %H:%M:%S')
            if key == "task_status":
                result["task_status_text"] = constants.TASK_STATUS_DICT[self.task_status]
            result[key] = value
        result["service_name"] = self.service.service_name
        return result

    @classmethod
    async def query(cls, session, actor_id=None, task_name=None, offset=None, limit=None):
        q = session.query(cls)
        if actor_id:
            q = q.filter(cls.actor_id == actor_id)
        if task_name:
            q = q.filter(cls.task_name.like(f'%{task_name}%'))
        q = q.filter(cls.delete_flag == False)
        total = q.count()
        if total:
            q = q.order_by(desc(cls.created_time))
            if offset:
                q = q.offset(offset)
            if limit:
                q = q.limit(limit)
        return total, q.all()


class BaiduPcTop50Condition(ProModel, ModelBase):
    """
    BaiduPcTop50Condition
    """
    __tablename__ = "baidu_pc_top50_condition"
    id = Column(Integer, primary_key=True)  # task id
    keywords = Column(String, nullable=false)  # 关键词
    query_limit = Column(Integer, default=50)  # 结果数，比如前50条
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建时间


class BaiduPcTop50Result(ProModel, ModelBase):
    """
    BaiduPcTop50Result
    """
    __tablename__ = "baidu_pc_top50_result"
    id = Column(Integer, primary_key=True)  # task id
    keyword = Column(String, nullable=false)  # 关键词
    rank = Column(Integer)  # 排名
    site_url = Column(String)  # 网址
    page_url = Column(String)  # 网页地址
    page_title = Column(String)  # 网页标题
    weight = Column(String)  # 权重
    top100 = Column(Integer)  # 此网站在百度排名前100名的关键词数量
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建时间
