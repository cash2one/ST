$(function () {
    $('#tablelist').bootstrapTable({
        url: "/admin/order/list",
        dataType: "json",
        pagination: true, //分页
        striped: true,
        sidePagination: "server", //服务端处理分页
        columns: [
            {
                title: '序号',
                align: 'center',
                valign: 'middle',
                formatter: function (value, row, index) {
                    var pageSize = $('#tablelist').bootstrapTable('getOptions').pageSize;//通过表的#id 可以得到每页多少条
                    var pageNumber = $('#tablelist').bootstrapTable('getOptions').pageNumber;//通过表的#id 可以得到当前第几页
                    return pageSize * (pageNumber - 1) + index + 1
                }
            }, {
                field: 'id',
                title: '订单编号',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'actor_phone',
                title: '手机号',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'service_name',
                title: '服务名称',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'package_name',
                title: '套餐信息',
                align: 'center',
                valign: 'middle',
                formatter: function (value, row, index) {
                    return value + '：￥' + row.package_price + '元/' + row.package_times + '次';
                }
            }, {
                field: 'payment_type',
                title: '支付方式',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'payment_price',
                title: '支付金额',
                align: 'center',
                valign: 'middle'
            },
            {
                field: 'payment_time',
                title: '支付时间',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'order_status_text',
                title: '订单状态',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'created_time',
                title: '创建时间',
                align: 'center',
                valign: 'middle'
            }, {
                title: '操作',
                field: 'id',
                align: 'center',
                valign: 'middle',
                formatter: function (value, row, index) {
                    if (row.order_status == 11)
                        return '<a href="javascript:;" onclick="check(\'' + row.id + '\')">审核</a> ';
                }
            }],
    });

    $("#btn_search").click(function () {
        var username = $("#username").val();
        var limit = $('#tablelist').bootstrapTable('getOptions').pageSize;
        $('#tablelist').bootstrapTable("refresh", {query: {phone: username, offset: 0, limit: limit}});
    });

    laydate.render({
        elem: '#payment_time'
        , type: 'datetime'
    });

    $("#btn_order_check").click(function () {
        var payment_type = $("#payment_type").val();
        var payment_price = $("#payment_price").val();
        var payment_time = $("#payment_time").val();
        if (payment_type == "" || payment_price == "" || payment_time == "") {
            layer.msg("请全部填写！");
            return;
        }

        $.post('/admin/order/' + order_check_id + '/check', {
            "payment_type": payment_type,
            "payment_price": payment_price,
            "payment_time": payment_time
        }, function (data) {
            if (data.code == 200) {
                layer.alert("审核成功！");
                layer.close(order_check_lay_id);
                $('#tablelist').bootstrapTable("refresh");
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json");
    });
});

var order_check_lay_id = "";
var order_check_id = "";

function check(order_id) {
    order_check_id = order_id;
    order_check_lay_id = layer.open({
        title: '订单审核',
        type: 1,
        skin: 'layui-layer-demo', //样式类名
        closeBtn: 1, //不显示关闭按钮
        anim: 2,
        shadeClose: true, //开启遮罩关闭
        content: $('#order_check'),
        area: ['450px', '280px'],
        end: function () {
            $("#order_check_form")[0].reset();
            order_check_id = "";
            order_check_lay_id = "";
        }
    });
}