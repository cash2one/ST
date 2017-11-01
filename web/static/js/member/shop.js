var layer0 = "";
$(function () {
    $("#btn_buynow").click(function () {
        layer0 = layer.open({
            title: '选择套餐',
            type: 1,
            skin: 'layui-layer-demo', //样式类名
            closeBtn: 0, //不显示关闭按钮
            anim: 2,
            shadeClose: true, //开启遮罩关闭
            content: $('#packages').html(),
            area: ['350px', '230px'],
            offset: ['150px', '465px'],
            end: function () {
                package_id = "";
                total_price = 0;
            }
        });
    });
});

var package_id = "";
var total_price = 0;

//选择套餐
function check_package(obj) {
    $(obj).addClass("active").children(":last").html('<i class="fa fa-check text-navy"></i>');
    $(obj).siblings().removeClass("active").children(":last").html('');
    package_id = $(obj).attr("pid");
    total_price = $(obj).attr("price");
    $(obj).parent().parent().next().find("span").html(total_price)
}

function buy_now() {
    if (package_id == "") {
        layer.msg('请选择套餐');
        return;
    }
    var service_id = $("#hidden_service_id").val();
    if (service_id == "") {
        layer.alert("参数异常，请尝试刷新页面后重新操作！");
        return;
    }
    layer.close(layer0);
    $.post('/member/shop/service/' + service_id + '/' + package_id + '/buynow', {}, function (data) {
        if (data.code == 200) {
            var package = data.data;
            $("#package_pay_service_name").html(package.service_name);
            $("#package_pay_package_name").html(package.package_name);
            $("#package_pay_price").html('￥' + package.package_price + '/' + package.times + '次');
            layer.open({
                title: '套餐支付',
                type: 1,
                skin: 'layui-layer-demo', //样式类名
                closeBtn: 1, //不显示关闭按钮
                anim: 2,
                shadeClose: false, //开启遮罩关闭
                content: $('#package_pay').html(),
                area: ['800px', '600px']
            });
        } else if (data.code == 2001) {
            layer.alert('服务购买成功，前往我的服务查看！');
        } else {
            layer.alert(data.message);
        }
    }, "json");
}