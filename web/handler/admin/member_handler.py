from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_admin_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.actor import Actor
from web.models.service import ActorService
from web.auth import admin_login_required


@st_admin_blueprint.route("/member", methods=["GET"])
@admin_login_required
async def index(request):
    return html(await render_template('/admin/member.html', request=request))


@st_admin_blueprint.route("/member/list", methods=["GET"])
@admin_login_required
async def get_member_list(request):
    offset = request.args.get("offset")
    limit = request.args.get("limit")
    phone = request.args.get("phone")
    if offset:
        offset = int(offset)
    if limit:
        limit = int(limit)
    with yhk_session() as session:
        data, total = await Actor.query(session, phone, offset, limit)
        actors = [actor.to_json() for actor in data]
        return json({"rows": actors, "total": total})


@st_admin_blueprint.route("/member/<actor_id:int>/lock", methods=["POST"])
@admin_login_required
async def get_member_list(request, actor_id):
    with yhk_session() as session:
        actor = await Actor.get(session, actor_id)
        if not actor:
            return json({"code": 500, "message": "会员信息不存在！"})
        actor.is_locked = not actor.is_locked
        session.commit()
    return json({"code": 200, "message": "操作成功！"})


@st_admin_blueprint.route("/member/<actor_id:int>/service", methods=["GET"])
@admin_login_required
async def member_service(request, actor_id):
    with yhk_session() as session:
        actor = await Actor.get(session, actor_id)
        datalist = await ActorService.get_member_services(session, actor_id)
        return html(
            await render_template('/admin/member_service.html', request=request, actor=actor, datalist=datalist))
