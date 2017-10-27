$(function () {
    $("#login_form").validate({
        submitHandler: function (form) {
            login();
        },
        rules: {
            username: {
                required: true,
                rangelength: [6, 10]
            },
            password: {
                required: true,
                rangelength: [6, 10]
            }
        }
    });


    function login() {
        var username = $("#username").val();
        var password = $("#password").val();
        var encrypt_password = md5(password);
        var post_data = {
            "username": username,
            "password": encrypt_password,
        }
        $.post("/admin/login", post_data, function (data) {
            if (data.code == 200) {
                location.href = "/admin/index";
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json");
    };
});