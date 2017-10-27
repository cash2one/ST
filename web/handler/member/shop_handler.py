from sanic.response import html, json
from yhklibs.web.prosanic.template import render_template
from web.handler.base import st_member_blueprint
from yhklibs.db.postgresql import yhk_session
from web.models.service import Service, ServicePackageBuyingLog, Package, ActorService
from web.models.order import ServiceOrder
from web.auth import login_required
from web.core import constants
import datetime


@st_member_blueprint.route("/shop", methods=["GET"])
@login_required
async def shop_index(request):
    with yhk_session() as session:
        services = await Service.get_all(session)
        for s in services:
            s.package = await Package.get_service_marked_price(session, s.id)
        return html(
            await render_template(
                "member/shop.html",
                request=request,
                datalist=services
            )
        )


@st_member_blueprint.route("/shop/service/<service_id:int>", methods=["GET"])
@login_required
async def service_detail(request, service_id):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    with yhk_session() as session:
        # 获取服务详情，服务套餐中排除不可用以及不可重复购买的套餐
        service = await Service.get(session, service_id)
        if not service.enable or service.delete_flag:
            return html(
                await render_template(
                    "500.html",
                    request=request,
                    message="服务不可用！"
                )
            )
        # 获取标价套餐
        service.package = await Package.get_service_marked_price(session, service.id)
        # 获取可售套餐
        packages = []
        for pk in service.packages:
            if pk.enable:
                if pk.can_buy_again:
                    packages.append(pk)
                else:
                    buying_log = await ServicePackageBuyingLog.check_can_buy_again(session, actor_id, pk.id)
                    if not buying_log:  # 未购买过此套餐
                        packages.append(pk)
        return html(
            await render_template(
                "member/shop_service.html",
                request=request,
                item=service,
                packages=packages
            )
        )


@st_member_blueprint.route("/shop/service/<service_id:int>/<package_id:int>/buynow", methods=["POST"])
@login_required
async def service_detail(request, service_id, package_id):
    actor = request["session"]["st_token"]
    actor_id = actor["id"]
    with yhk_session() as session:
        service = await Service.get(session, service_id)
        if not service:
            return json({"code": 500, "message": "服务信息异常，请联系客服！"})
        package = await Package.get(session, package_id)
        if not package or not package.enable:
            return json({"code": 500, "message": "服务信息异常，请联系客服！"})
        if package.service_id != service_id:
            return json({"code": 500, "message": "服务信息异常，请联系客服！"})
        if not package.can_buy_again:
            buying_log = await ServicePackageBuyingLog.check_can_buy_again(session, actor_id, package_id)
            if buying_log:
                return json({"code": 500, "message": "您已购买过此套餐，不可重复购买！"})

        code = 200
        now = datetime.datetime.now()
        service_order = ServiceOrder()
        service_order.actor_id = actor_id  # 用户id
        service_order.service_id = service_id  # 服务id
        service_order.package_id = package_id  # 套餐id
        service_order.order_status = constants.ORDER_STATUS_CONFIRM  # 订单状态 1：已确认，2：已取消，3：已退货
        if package.package_type == constants.SERVICE_PACKAGE_TYPE_FREE:
            service_order.payment_type = constants.PAYMENT_TYPE_FREE
            service_order.payment_price = package.package_price  # 实际支付金额
            service_order.payment_time = now
            service_order.payment_status = constants.PAYMENT_STATUS_PAYED  # 支付状态 1：未支付，2：已支付，3：已退款
        else:
            service_order.payment_status = constants.PAYMENT_STATUS_UNPAYED  # 支付状态 1：未支付，2：已支付，3：已退款
        session.add(service_order)
        session.commit()
        if package.package_type == constants.SERVICE_PACKAGE_TYPE_FREE:
            # 创建购买记录
            log = ServicePackageBuyingLog()
            log.actor_id = actor_id
            log.service_id = service_id
            log.package_id = package_id
            log.payment_price = package.package_price
            log.service_order_id = service_order.id
            log.created_time = now
            session.add(log)
            session.commit()
            # 添加我的服务信息
            actor_service = await ActorService.get_my_service(session, actor_id, service_id)
            if actor_service:
                actor_service.last_buy_time = now
                actor_service.package_time += package.times
            else:
                actor_service = ActorService()
                actor_service.actor_id = actor_id
                actor_service.service_id = service_id
                actor_service.service_name = service.service_name
                actor_service.last_buy_time = now
                actor_service.package_time = package.times
                actor_service.created_time = now
                session.add(actor_service)
            session.commit()
            code = 2001

        return json({"code": code, "data": {"service_name": service.service_name, "package_name": package.package_name,
                                            "package_price": package.package_price, "times": package.times}})
