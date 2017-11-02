from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_admin_blueprint
from web.auth import admin_login_required


@st_admin_blueprint.route("/index", methods=["GET"])
@admin_login_required
async def index(request):
    return html(await render_template('/admin/index.html', request=request))


@st_admin_blueprint.route("/workbench", methods=["GET"])
@admin_login_required
async def workbench(request):
    return html(await render_template('/admin/workbench.html', request=request))