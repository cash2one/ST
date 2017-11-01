from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.actor import Actor
from web.auth import login_required
from web.models.service import ServiceConsumeLog


@st_member_blueprint.route("/service", methods=["GET"])
@login_required
async def login(request):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    with yhk_session() as session:
        actor = await Actor.get(session, actor_id)
        services = actor.services
        return html(
            await render_template(
                "member/my_service.html",
                request=request,
                datalist=services
            )
        )


@st_member_blueprint.route("/service/consume_log/<service_id:int>", methods=["GET"])
@login_required
async def consume_log_index(request, service_id):
    return html(
        await render_template(
            "member/my_service_consume_log.html",
            request=request,
            service_id=service_id
        )
    )


@st_member_blueprint.route("/service/consume_log/<service_id:int>/list", methods=["GET"])
@login_required
async def consume_log_list(request, service_id):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]

    offset = request.args.get("offset")
    limit = request.args.get("limit")
    if offset:
        offset = int(offset)
    if limit:
        limit = int(limit)

    with yhk_session() as session:
        total, logs = await ServiceConsumeLog.query(session, actor_id, service_id, offset, limit)
        rows = [log.to_json() for log in logs]
        return json({"rows": rows, "total": total})
