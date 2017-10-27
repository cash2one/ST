from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_admin_blueprint
import hashlib
from yhklibs.db.postgresql import yhk_session
from web.models.sysuser import SysUser


@st_admin_blueprint.route("/login", methods=["GET", "POST"])
async def login(request):
    if request.method == "GET":
        return html(await render_template('/admin/login.html', request=request))
    username = request.form.get("username")  # 手机号
    password = request.form.get("password")  # 密码，md5加密
    if not (username and password):
        return json({"code": 500, "message": "请填写登录信息！"})
    if len(username) < 6 or len(username) > 10:
        return json({"code": 500, "message": "用户名或密码错误！"})
    if len(password) != 32:
        return json({"code": 500, "message": "用户名或密码错误！"})

    with yhk_session() as session:
        user = await SysUser.get_by_username(session, username)
        if not user:
            return json({"code": 500, "message": "用户名或密码错误！"})
        encrypt_pwd = hashlib.md5(f"{username}:{password}".encode("utf-8")).hexdigest()
        if user.password != encrypt_pwd:
            return json({"code": 500, "message": "用户名或密码错误！"})

        request["session"]["st_admin_token"] = user.to_json()
        return json({"code": 200, "message": "登录成功！"})
