from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.service import ActorService
from web.models.task import Task, BaiduPcTop50Condition
from web.auth import login_required
from web.core import constants
from web.core.api import baidu_keyword_rank_pc


@st_member_blueprint.route("/task", methods=["GET"])
@login_required
async def task_index(request):
    return html(
        await render_template(
            "member/my_task.html",
            request=request
        )
    )


@st_member_blueprint.route("/task/list", methods=["GET"])
@login_required
async def task_list(request):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]

    offset = request.args.get("offset")
    limit = request.args.get("limit")
    task_name = request.args.get("task_name")
    if offset:
        offset = int(offset)
    if limit:
        limit = int(limit)

    with yhk_session() as session:
        total, tasks = await Task.query(session, actor_id, task_name, offset, limit)
        rows = [await task.to_json(session) for task in tasks]
        return json({"rows": rows, "total": total})


@st_member_blueprint.route("/task/create", methods=["GET"])
@login_required
async def task_create(request):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    with yhk_session() as session:
        services = await ActorService.get_member_services(session, actor_id)
        return html(
            await render_template(
                "member/task_create.html",
                request=request,
                services=services
            )
        )


@st_member_blueprint.route("/task/<task_type:int>/save", methods=["POST"])
@login_required
async def task_save(request, task_type):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    task_name = request.form.get("task_name")
    if not task_name:
        return json({"code": 500, "message": "请填写任务名称！"})
    if task_type == constants.SERVICE_TYPE_BAIDU_PC_TOP50:
        keywords = request.form.get("keywords")
        if not keywords:
            return json({"code": 500, "message": "请填写关键词！"})
        keywords = keywords.strip("\n").replace("\n", "|")
        task_count = request.form.get("task_count")
        if task_count:
            task_count = int(task_count)
        with yhk_session() as session:
            # 检查是否拥有此服务权限
            actor_service = await ActorService.get_service_by_type(session, actor_id, task_type)
            if not actor_service:
                return json({"code": 401, "message": "抱歉，没有服务权限，请先购买此服务！"})
            task = await Task.create_task(session, actor_id, task_name, actor_service.service_id, task_type)
            condition = await BaiduPcTop50Condition.create_condition(session, task.id, keywords, task_count)
            # 启动任务
            out_task_id, result = baidu_keyword_rank_pc.create_task(keywords, task_count)
            task.task_status = constants.TASK_STATUS_START
            task.out_task_id = out_task_id
            task.task_result = result
            session.add(task)
            session.commit()
            return json({"code": 200, "message": "创建成功！"})
