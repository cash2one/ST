import datetime
from sqlalchemy import *
from yhklibs.db.postgresql import ModelBase, ProModel
from web.core import constants
from sqlalchemy.orm import relationship
from web.core.api import baidu_keyword_rank_pc


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
    delete_flag = Column(Boolean, default=False)  # 删除标志
    out_task_id = Column(String)  # 商户任务id

    service = relationship("Service")

    async def to_json(self, session):
        await self.check_task_status(session)
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

    async def check_task_status(self, session):
        if self.task_status == constants.TASK_STATUS_FINISH:
            return
        data, r, code = baidu_keyword_rank_pc.get_task_data(self.out_task_id)
        self.task_result = r
        if code == '0':
            self.task_status = constants.TASK_STATUS_FINISH
            session.commit()
            await BaiduPcTop50Result.save_result(session, self.id, data)

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

    @classmethod
    async def create_task(cls, session, actor_id, task_name, service_id, service_type, ):
        task = cls()
        task.actor_id = actor_id
        task.task_name = task_name
        task.task_status = constants.TASK_STATUS_INIT
        task.service_id = service_id
        task.service_type = service_type
        session.add(task)
        session.commit()
        return task


class BaiduPcTop50Condition(ProModel, ModelBase):
    """
    BaiduPcTop50Condition
    """
    __tablename__ = "baidu_keyword_rank_pc_condition"
    id = Column(Integer, primary_key=True)  # task id
    keywords = Column(String, nullable=false)  # 关键词
    query_limit = Column(Integer, default=50)  # 结果数，比如前50条
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建时间

    @classmethod
    async def create_condition(cls, session, task_id, keywords, query_limit):
        con = cls()
        con.id = task_id
        con.keywords = keywords
        if query_limit:
            con.query_limit = query_limit
        session.add(con)
        session.commit()
        return con


class BaiduPcTop50Result(ProModel, ModelBase):
    """
    BaiduPcTop50Result
    """
    __tablename__ = "baidu_keyword_rank_pc_result"
    id = Column(Integer, Sequence("baidu_keyword_rank_pc_result_id_seq", start=100000), primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    keyword = Column(String, nullable=false)  # 关键词
    rank = Column(Integer)  # 排名
    site_url = Column(String)  # 网址
    page_url = Column(String)  # 网页地址
    page_title = Column(String)  # 网页标题
    weight = Column(String)  # 权重
    top100 = Column(Integer)  # 此网站在百度排名前100名的关键词数量
    created_time = Column(DateTime, default=datetime.datetime.now)  # 创建时间

    @classmethod
    async def save_result(cls, session, task_id, data):
        count = session.query(cls).filter(cls.task_id == task_id).count()
        if count > 0:
            return
        now = datetime.datetime.now()
        for item in data:
            result = cls()
            result.task_id = task_id
            result.keyword = item.get("keyword")
            result.rank = item.get("rank")
            result.site_url = item.get("site_url")
            result.page_url = item.get("page_url")
            result.page_title = item.get("page_title")
            result.weight = item.get("site_weight")
            result.top100 = item.get("top100")
            result.created_time = now
            session.add(result)
        session.commit()
