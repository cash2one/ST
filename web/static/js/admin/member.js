$(function () {
    $('#tablelist').bootstrapTable({
        url: "/admin/member/list?t=" + new Date().getTime(),
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
                field: 'username',
                title: '手机号',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'is_locked',
                title: '锁定',
                align: 'center',
                valign: 'middle',
                formatter: function (value, row, index) {
                    return value ? '<span class="glyphicon glyphicon-ok"></span>' : '<span class="glyphicon glyphicon-remove"></span>';
                }
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
                    var txt = row.is_locked ? "取消锁定" : "锁定";
                    var lock = '<a style="margin-right: 20px;" href="#" mce_href="#" onclick="lock(\'' + value + '\',' + row.is_locked + ')">' + txt + '</a>';
                    var view = '<a href="/admin/member/' + value + '/service">查看服务</a> ';
                    return lock + view;
                }
            }],
    });

    $("#btn_search").click(function () {
        var username = $("#username").val();
        var limit = $('#tablelist').bootstrapTable('getOptions').pageSize;
        $('#tablelist').bootstrapTable("refresh", {query: {phone: username, offset: 0, limit: limit}});
    });
});

function lock(actor_id, is_locked) {
    var txt = is_locked ? "取消锁定" : "锁定";
    layer.confirm('确定要' + txt + '吗？', {
        btn: ['是', '否'] //按钮
    }, function () {
        $.post("/admin/member/" + actor_id + "/lock", {}, function (data) {
            if (data.code == 200) {
                layer.alert(txt + "成功！");
                $('#tablelist').bootstrapTable("refresh");
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json");
    });
}