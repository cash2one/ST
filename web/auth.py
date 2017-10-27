from functools import wraps
from yhklibs.web.prosanic import YHKRequest
from yhklibs.web.prosanic.response import redirect


def login_required(func):
    @wraps(func)
    def decorated_view(request, *args, **kwargs):
        if request.method in ["OPTIONS", ]:
            return func(*args, **kwargs)
        st_token = request["session"].get("st_token")
        if not st_token:
            return redirect("/member/login")
        return func(request, *args, **kwargs)

    return decorated_view


def admin_login_required(func):
    @wraps(func)
    def decorated_view(request, *args, **kwargs):
        if request.method in ["OPTIONS", ]:
            return func(*args, **kwargs)
        st_token = request["session"].get("st_admin_token")
        if not st_token:
            return redirect("/admin/login")
        return func(request, *args, **kwargs)

    return decorated_view

async def load_from_cookie(request: YHKRequest):
    """
    从cookie登录
    :param request:
    :return:
    """
    pass
