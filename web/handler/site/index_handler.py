from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_web_blueprint


@st_web_blueprint.route("/", methods=["GET"])
async def index(request):
    return html(await render_template('/site/index.html', request=request))
