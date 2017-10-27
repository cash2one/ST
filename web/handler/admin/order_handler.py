from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_admin_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.order import ServiceOrder
from web.auth import admin_login_required
from web.core import constants
from web.models.service import ServicePackageBuyingLog, ActorService
import datetime


@st_admin_blueprint.route("/order", methods=["GET"])
@admin_login_required
async def index(request):
    return html(await render_template('/admin/order.html', request=request))


@st_admin_blueprint.route("/order/list", methods=["GET"])
@admin_login_required
async def get_order_list(request):
    offset = request.args.get("offset")
    limit = request.args.get("limit")
    phone = request.args.get("phone")
    if offset:
        offset = int(offset)
    if limit:
        limit = int(limit)
    with yhk_session() as session:
        data, total = await ServiceOrder.query(session, phone, offset, limit)
        orders = []
        for item in data:
            order_status = int(f'{item.order_status}{item.payment_status}')
            orders.append({
                "id": item.id,
                "actor_id": item.actor_id,
                "service_id": item.service_id,
                "package_id": item.package_id,
                "actor_phone": item.actor.phone,
                "service_name": item.service.service_name,
                "package_name": item.package.package_name,
                "package_price": item.package.package_price,
                "package_times": item.package.times,
                "payment_type": constants.PAYMENT_TYPE_MAP.get(item.payment_type),
                "payment_price": item.payment_price,
                "payment_time": item.payment_time.strftime('%Y-%m-%d %H:%M:%S') if item.payment_time else None,
                "order_status": order_status,
                "order_status_text": constants.ORDER_STATUS_MAP.get(order_status),
                "created_time": item.created_time.strftime('%Y-%m-%d %H:%M:%S')
            })
        return json({"rows": orders, "total": total})


@st_admin_blueprint.route("/order/<order_id:int>/check", methods=["POST"])
@admin_login_required
async def get_order_list(request, order_id):
    payment_type = request.form.get("payment_type")
    payment_price = request.form.get("payment_price")
    payment_time = request.form.get("payment_time")
    if not (payment_type and payment_price and payment_time):
        return json({"code": 500, "message": "参数错误，请填写完整信息！"})
    payment_type = int(payment_type)
    payment_price = float(payment_price)
    payment_time = datetime.datetime.strptime(payment_time, "%Y-%m-%d %H:%M:%S")
    with yhk_session() as session:
        # 修改订单支付信息，并增加相应服务次数
        order = await ServiceOrder.get(session, order_id)
        if not order.service or not order.package:
            return json({"code": 500, "message": "订单服务套餐不存在！"})
        if order.payment_status != constants.PAYMENT_STATUS_UNPAYED and order.order_status != constants.ORDER_STATUS_CONFIRM:
            return json({"code": 500, "message": "订单已支付，不能重复审核！"})
        if order.package.service_id != order.service_id:
            return json({"code": 500, "message": "订单服务和套餐不匹配！"})
        if not order.package.can_buy_again:
            buying_log = await ServicePackageBuyingLog.check_can_buy_again(session, order.actor_id, order.package_id)
            if buying_log:
                return json({"code": 500, "message": "此用户已购买过此套餐，不可重复购买！"})

        now = datetime.datetime.now()
        order.payment_price = payment_price  # 实际支付金额
        order.payment_time = payment_time
        order.payment_status = constants.PAYMENT_STATUS_PAYED  # 支付状态 1：未支付，2：已支付，3：已退款
        order.payment_type = payment_type

        # 创建购买记录
        log = ServicePackageBuyingLog()
        log.actor_id = order.actor_id
        log.service_id = order.service.id
        log.package_id = order.package_id
        log.payment_price = payment_price
        log.service_order_id = order_id
        log.created_time = now
        session.add(log)

        # 添加我的服务信息
        actor_service = await ActorService.get_my_service(session, order.actor_id, order.service_id)
        if actor_service:
            actor_service.last_buy_time = now
            actor_service.package_time += order.package.times
        else:
            actor_service = ActorService()
            actor_service.actor_id = order.actor_id
            actor_service.service_id = order.service_id
            actor_service.service_name = order.service.service_name
            actor_service.last_buy_time = now
            actor_service.package_time = order.package.times
            actor_service.created_time = now
            session.add(actor_service)
        session.commit()
        return json({"code": 200, "message": "审核成功！"})
