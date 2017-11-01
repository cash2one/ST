from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.service import ActorService
from web.models.task import Task, BaiduPcTop50Condition, BaiduPcTop50Result
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
    service_id = request.args.get("service_id")
    with yhk_session() as session:
        services = await ActorService.get_member_services(session, actor_id)
        return html(
            await render_template(
                "member/task_create.html",
                request=request,
                services=services,
                service_id=service_id
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
        keywords_arr = keywords.split("|")
        times = len(keywords_arr)
        if times > 50:
            return json({"code": 500, "message": "关键词最多50个！"})
        task_count = request.form.get("task_count")
        if task_count:
            task_count = int(task_count)
            if task_count > 100:
                return json({"code": 500, "message": "查询结果最多返回前100名！"})
        with yhk_session() as session:
            # 检查是否拥有此服务权限
            actor_service = await ActorService.get_service_by_type(session, actor_id, task_type)
            if not actor_service:
                return json({"code": 401, "message": "抱歉，没有服务权限，请先购买此服务！"})
            # 检查服务次数是否足够
            if actor_service.package_time < times:
                return json({"code": 500, "message": "抱歉，服务调用次数不足，请先购买！"})
            # 首先扣除服务次数
            actor_service.package_time = actor_service.package_time - times
            session.commit()
            # 创建任务
            task = await Task.create_task(session, actor_id, task_name, actor_service.service_id, task_type)
            await BaiduPcTop50Condition.create_condition(session, task.id, keywords, task_count)
            # 启动任务
            out_task_id, result, code = 83317, {}, 0  # baidu_keyword_rank_pc.create_task(keywords, task_count)
            if code == 0:
                task.task_status = constants.TASK_STATUS_START
            else:
                task.task_status = constants.TASK_STATUS_FAIL
                # 将服务次数加回来
                actor_service.package_time = actor_service.package_time + times
            task.out_task_id = out_task_id
            task.task_result = result
            session.commit()
            return json({"code": 200, "message": "创建成功！"})
    return json({"code": 500, "message": "此类型服务暂不支持！"})


@st_member_blueprint.route("/task/<task_id:int>/delete", methods=["POST"])
@login_required
async def task_delete(request, task_id):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    with yhk_session() as session:
        task = await Task.get(session, task_id)
        if not task:
            return json({"code": 500, "message": "任务不存在！"})
        if task.actor_id != actor_id:
            return json({"code": 401, "message": "没有权限，此任务不属于你！"})
        task.delete_flag = True
        session.commit()
    return json({"code": 200, "message": "删除成功！"})


@st_member_blueprint.route("/task/<task_id:int>/view", methods=["GET"])
@login_required
async def task_save(request, task_id):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    with yhk_session() as session:
        task = await Task.get(session, task_id)
        condition = None
        service_type = constants.SERVICE_TYPE_BAIDU_PC_TOP50
        if task:
            if task.actor_id != actor_id:
                task = None
            else:
                task.task_status_text = constants.TASK_STATUS_DICT.get(task.task_status)
                if task.service_type == constants.SERVICE_TYPE_BAIDU_PC_TOP50:
                    condition = await BaiduPcTop50Condition.get(session, task_id)
                service_type = task.service_type
        return html(
            await render_template(
                f"member/task_view_{service_type}.html",
                request=request,
                task=task,
                condition=condition
            )
        )


@st_member_blueprint.route("/task/<task_id:int>/result", methods=["GET"])
@login_required
async def task_result(request, task_id):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    with yhk_session() as session:
        task = await Task.get(session, task_id)
        service_type = constants.SERVICE_TYPE_BAIDU_PC_TOP50
        if task:
            if task.actor_id != actor_id:
                task = None
            else:
                service_type = task.service_type
        return html(
            await render_template(
                f"member/task_result_{service_type}.html",
                request=request,
                task=task
            )
        )


@st_member_blueprint.route("/task/<task_type:int>/<task_id:int>/list", methods=["GET"])
@login_required
async def task_result_list(request, task_type, task_id):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    offset = request.args.get("offset")
    limit = request.args.get("limit")
    if offset:
        offset = int(offset)
    if limit:
        limit = int(limit)
    with yhk_session() as session:
        task = await Task.get(session, task_id)
        if not task or (task.actor_id != actor_id):
            return json({"rows": [], "total": 0})
        if task_type == constants.SERVICE_TYPE_BAIDU_PC_TOP50:
            total, rows = await BaiduPcTop50Result.query(session, task_id, offset, limit)
            rows = [item.to_json() for item in rows]
            return json({"rows": rows, "total": total})
