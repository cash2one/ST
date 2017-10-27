from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.actor import Actor
from web.auth import login_required


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