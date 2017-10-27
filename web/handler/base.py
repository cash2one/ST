from sanic import Blueprint

st_web_blueprint = Blueprint("st_web")
st_member_blueprint = Blueprint("st_member_web", "member")
st_admin_blueprint = Blueprint("st_admin", "admin")
