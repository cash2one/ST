$(function () {
    $("#register_form").validate({
        submitHandler: function (form) {
            register();
        },
        rules: {
            username: {
                required: true,
                checkPhone: true
            },
            password: {
                required: true,
                rangelength: [6, 10]
            },
            confirm_password: {
                equalTo: "#password"
            },
            sms_code: {
                required: true,
                digits: true,
                maxlength: 10
            }
        }
    });

    $.validator.addMethod("checkPhone", function (value, element, params) {
        return this.optional(element) || (tools.test_phone(value));
    }, "请输入正确的手机号码！");

    $("#btn_sms_code").click(function () {
        send_sms_code();
    });

    function send_sms_code() {
        var phone = $("#username").val();
        if (phone == "") {
            layer.tips('请填写手机号！', '#username');
            return;
        }
        if (!tools.test_phone(phone)) {
            layer.tips('手机号码格式不正确！', '#username');
            return;
        }
        $("#btn_sms_code").unbind("click");
        $("#btn_sms_code").html("发送中...")
        $.post("/member/register/sms/send", {"phone": phone}, function (data) {
            if (data.code == 200) {
                var count = 5;
                var timer_id = setInterval(function () {
                    $("#btn_sms_code").html(count + "s")
                    count -= 1;
                    if (count == 0) {
                        clearInterval(timer_id);
                        $("#btn_sms_code").html("再次获取")
                        $("#btn_sms_code").bind("click", function () {
                            send_sms_code();
                        });
                    }
                }, 1000);
            } else {
                layer.alert(data.message, {"icon": 2});
                $("#btn_sms_code").html("再次获取")
                $("#btn_sms_code").bind("click", function () {
                    send_sms_code();
                });
            }
        }, "json");
    };

    function register() {
        var username = $("#username").val();
        var password = md5($("#password").val());
        var confirm_password = md5($("#confirm_password").val());
        var sms_code = $("#sms_code").val();
        var content = {
            "username": username,
            "password": password,
            "confirm_password": confirm_password,
            "sms_code": sms_code
        };
        $.post("/member/register", content, function (data) {
            if (data.code == 200) {
                layer.msg("注册成功，前往登录...", {
                    icon: 16
                    , shade: 0.01
                }, function () {
                    location.href = "/member/login";
                });
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json");
    };
});