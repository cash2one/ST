from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.actor import Actor
from web.models.service import ActorService
from web.models.task import Task
from web.auth import login_required


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
        rows = [task.to_json() for task in tasks]
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
        return json({"code": 500, message: "请填写任务名称！"})
    task_name = request.form.get("task_name")
    task_name = request.form.get("task_name")

    with yhk_session() as session:
        actor = await Actor.get(session, actor_id)
        return html(
            await render_template(
                "member/task_create.html",
                request=request,
                services=actor.services
            )
        )
