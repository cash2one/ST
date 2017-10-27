var tools = {
    test_phone: function (value) {
        var phone_reg = /^1[34578]\d{9}$/;
        return phone_reg.test(value);
    }
};

$(function () {
    $(".ibox-tools .st-backward").click(function () {
        window.history.back();
    });

    $(".ibox-tools .st-refresh").click(function () {
        window.location.reload();
    });


    if (location.href.indexOf("login") > 0) {
        if (location.href != top.location.href) {
            top.location.href = location.href;
        }
    }
});