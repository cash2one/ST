from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
import hashlib
from yhklibs.db.postgresql import yhk_session
from web.models.actor import Actor
from web.core import tools
from sanic import response
from yhklibs.web.prosanic.response import redirect


@st_member_blueprint.route("/login", methods=["GET", "POST"])
async def login(request):
    if request.method == "GET":
        return html(await render_template('/member/login.html', request=request))
    username = request.form.get("username")  # 手机号
    password = request.form.get("password")  # 密码，md5加密
    valid_code = request.form.get("valid_code")  # 验证码
    if not (username and password and valid_code):
        return json({"code": 500, "message": "请填写登录信息！"})
    if not tools.test_mobile(username):
        return json({"code": 500, "message": "手机号码格式错误！"})
    session_valid_code = request["session"]["valid_code"]
    if len(valid_code) > 4 or session_valid_code != valid_code.upper():
        return json({"code": 500, "message": "验证码错误！"})

    with yhk_session() as session:
        actor = await Actor.get_by_phone(session, username)
        if not actor:
            return json({"code": 500, "message": "用户名或密码错误！"})
        encrypt_pwd = hashlib.md5(f"{username}:{password}".encode("utf-8")).hexdigest()
        if actor.password != encrypt_pwd:
            return json({"code": 500, "message": "用户名或密码错误！"})
        if actor.is_locked:
            return json({"code": 500, "message": "账户已锁定，请联系管理员！"})

        request["session"]["st_token"] = actor.to_json()
        return json({"code": 200, "message": "登录成功！"})


@st_member_blueprint.route("/valid_code", methods=["GET"])
async def valid_code(request):
    text, bytes = tools.generate_valid_code_image()
    request["session"]["valid_code"] = text

    async def streaming_fn(response):
        response.write(bytes)

    return response.stream(streaming_fn, content_type='image/png')


@st_member_blueprint.route("/logout", methods=["GET"])
async def logout(request):
    request["session"]["st_token"] = None
    return redirect("/member/login")
