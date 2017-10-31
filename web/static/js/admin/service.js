$(function () {
    $('#tablelist').bootstrapTable({
        url: "/admin/service/list?_time=" + new Date().getTime(),
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
                field: 'service_name',
                title: '服务名称',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'sub_heading',
                title: '副标题',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'price',
                title: '单价（元）',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'category_name',
                title: '所属分类',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'enable',
                title: '是否可用',
                align: 'center',
                valign: 'middle',
                formatter: function (value, row, index) {
                    return value ? '<span class="glyphicon glyphicon-ok"></span>' : '<span class="glyphicon glyphicon-remove"></span>';
                }
            }, {
                field: 'order_no',
                title: '排序',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'remark',
                title: '备注',
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
                    var v = '<a href="/admin/service/' + value + '/view">查看</a> ';
                    var e = '<a href="/admin/service/edit?service_id=' + value + '">编辑</a> ';
                    var d = '<a href="javascript:;" onclick="delete_service(\'' + row.id + '\')">删除</a> ';
                    return v + e + d;
                }
            }],
    });

    $("#btn_search").click(function () {
        var service_name = $("#service_name").val();
        var limit = $('#tablelist').bootstrapTable('getOptions').pageSize;
        $('#tablelist').bootstrapTable("refresh", {query: {service_name: service_name, offset: 0, limit: limit}});
    });

    //保存服务信息
    $("#btn_edit_save").click(function () {
        var service_id = $("#service_id").val();
        var service_name = $("#pl_service_info #service_name").val();
        var sub_heading = $("#pl_service_info #sub_heading").val();
        var price = $("#pl_service_info #price").val();
        var enable = $("#pl_service_info #enable").prop("checked");
        var category_id = $("#pl_service_info #category").val();
        var order_no = $("#pl_service_info #order_no").val();
        var remark = $("#pl_service_info #remark").val();
        var instruction = $("#pl_service_info #instruction").val();
        var service_type = $("#pl_service_info #service_type").val();
        var content = {
            service_id: service_id,
            service_name: service_name,
            sub_heading: sub_heading,
            price: price,
            enable: enable,
            category_id: category_id,
            order_no: order_no,
            remark: remark,
            instruction: instruction,
            service_type: service_type
        }

        $.post("/admin/service/edit", content, function (data) {
            if (data.code == 200) {
                layer.msg("保存成功！");
                $("#service_id").val(data.service_id);
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json");
    });

});

function delete_service(service_id) {
    layer.confirm('确定要删除吗？', {
        btn: ['是', '否'] //按钮
    }, function () {
        $.post('/admin/service/' + service_id + '/delete', {}, function (data) {
            if (data.code == 200) {
                layer.msg("删除成功！");
                $('#tablelist').bootstrapTable("refresh");
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json")
    });
}

function save_package(obj) {
    var form = $(obj).parent().parent().prev();
    var service_id = $("#service_id").val();
    var content = form.serialize() + "&service_id=" + service_id;
    $.post("/admin/service/package/save", content, function (data) {
        if (data.code == 200) {
            layer.msg("保存成功！");
            form.find('input[name="package_id"]').val(data.package_id);
        } else {
            layer.alert(data.message, {"icon": 2});
        }
    }, "json")
}

function delete_package(obj, obj2) {
    layer.confirm('确定要删除吗？', {
        btn: ['是', '否'] //按钮
    }, function () {
        var package_id = obj;
        if (typeof obj == "object") {
            package_id = $(obj).parent().parent().prev().find('input[name="package_id"]').val();
            if (package_id == "") {
                layer.msg("删除失败！");
            }
        }
        $.post('/admin/service/package/' + package_id + '/delete', {}, function (data) {
            if (data.code == 200) {
                layer.msg("删除成功！");
                if (typeof obj == "object") {
                    $(obj).parent().parent().parent().parent().remove();
                } else {
                    $(obj2).parent().parent().parent().parent().remove();
                }
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json");
    });
}

function add_package_tpl(obj) {
    var tpl = $("#package_add_tpl").html();
    $(obj).parent().before(tpl);
}