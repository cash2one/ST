$(function () {
    $("#login_form").validate({
        submitHandler: function (form) {
            login();
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
            valid_code: {
                required: true,
                maxlength: 4
            }
        }
    });

    $.validator.addMethod("checkPhone", function (value, element, params) {
        return this.optional(element) || (tools.test_phone(value));
    }, "请输入正确的手机号码！");


    $("#img_valid").attr("src", "/member/valid_code?t=" + Date.parse(new Date()));
    $("#img_valid").click(function () {
        $(this).attr("src", "/member/valid_code?t=" + Date.parse(new Date()));
    });


    function login() {
        var username = $("#username").val();
        var password = $("#password").val();
        var encrypt_password = md5(password);
        var valid_code = $("#valid_code").val();
        var post_data = {
            "username": username,
            "password": encrypt_password,
            "valid_code": valid_code
        }
        $.post("/member/login", post_data, function (data) {
            if (data.code == 200) {
                location.href = "/member/index";
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json");
    };

});