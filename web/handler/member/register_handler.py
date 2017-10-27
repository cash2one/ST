from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.actor import Actor
from web.core.jpush_sms import Jpush
from web.core.tools import test_mobile
import hashlib


@st_member_blueprint.route("/register", methods=["GET", "POST"])
async def register(request):
    if request.method == "GET":
        return html(await render_template('/member/register.html', request=request))
    username = request.form.get("username")  # 手机号
    password = request.form.get("password")  # 密码，md5加密
    confirm_password = request.form.get("confirm_password")  # 密码，md5加密
    sms_code = request.form.get("sms_code")
    if not (username and password and confirm_password and sms_code):
        return json({"code": 500, "message": "请填写完成信息！"})
    if not test_mobile(username):
        return json({"code": 500, "message": "手机号码不正确！"})
    if password != confirm_password:
        return json({"code": 500, "message": "两次密码不一致！"})
    if len(sms_code) > 10:
        return json({"code": 500, "message": "验证码长度不可超过10位！"})

    msg_id = request["session"].get("sms_code_id")
    if not msg_id:
        return json({"code": 500, "message": "验证码错误！"})
    # valid_sms_code = Jpush().valid_sms_txt_codes(msg_id, sms_code)
    # if not valid_sms_code:
    #     return json({"code": 500, "message": "验证码不正确！"})
    with yhk_session() as session:
        actor = await Actor.get_by_phone(session, username)
        if actor:
            return json({"code": 500, "message": "手机号码已注册！"})

        src_pwd = f"{username}:{password}".encode("utf-8")
        encrypt_pwd = hashlib.md5(src_pwd).hexdigest()

        actor = Actor()
        actor.phone = username
        actor.password = encrypt_pwd
        session.add(actor)
        session.commit()
        return json({"code": 200, "message": "注册成功！"})


@st_member_blueprint.route("/register/sms/send", methods=["POST"])
async def sms_send(request):
    phone = request.form.get("phone")  # 手机号
    if not phone:
        return json({"code": 500, "message": "手机号码为空！"})
    if not test_mobile(phone):
        return json({"code": 500, "message": "手机号码不正确！"})
    # 1.检查手机号是否已经注册过
    with yhk_session() as session:
        actor = await Actor.get_by_phone(session, phone)
        if actor:
            return json({"code": 500, "message": "手机号码已注册！"})
    msg_id = "354838553987"  # Jpush().send_sms_txt_codes(phone)
    if not msg_id:
        return json({"code": 500, "message": "获取验证码失败！"})
    request["session"]["sms_code_id"] = msg_id
    return json({"code": 200, "message": "发送成功！"})
