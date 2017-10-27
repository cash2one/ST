import os

from web.handler.base import st_web_blueprint, st_admin_blueprint, st_member_blueprint
from yhklibs.web.prosanic import ProSanic
from yhklibs.web.prosanic.response import text
from yhklibs.web.prosanic.template import add_template_path

prosanic = ProSanic("st")

# 注册蓝图

prosanic.blueprint(st_web_blueprint)
prosanic.blueprint(st_admin_blueprint)
prosanic.blueprint(st_member_blueprint)

# 注册静态文件路径
cur_dir = os.path.dirname(os.path.abspath(__file__))
prosanic.static("/static", os.path.join(cur_dir, "static"))
prosanic.static("/favicon.ico", os.path.join(cur_dir, "static/favicon.ico"))

cur_dir = os.path.dirname(os.path.abspath(__file__))
add_template_path(os.path.join(cur_dir, "./templates"))


@prosanic.route("/ping")
async def ping(request):
    return text("pong")


# context
@prosanic.middleware("request")
async def prepare_request_context(request):
    # await load_from_cookie(request)
    pass
