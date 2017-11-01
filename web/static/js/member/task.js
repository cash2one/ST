$(function () {
    $('#tablelist').bootstrapTable({
        url: "/member/task/list?_time=" + new Date().getTime(),
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
                title: '任务id',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'task_name',
                title: '任务名称',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'service_name',
                title: '服务名称',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'task_status_text',
                title: '任务状态',
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
                    var v = '<a href="/member/task/' + value + '/view">详情</a> ';
                    var d = '<a href="javascript:;" onclick="delete_task(\'' + value + '\')">删除</a> ';
                    var r = '<a href="/member/task/' + value + '/result">查看结果</a> ';
                    return v + d + r;
                }
            }],
    });

    $("#btn_search").click(function () {
        var task_name = $("#task_name").val();
        var limit = $('#tablelist').bootstrapTable('getOptions').pageSize;
        $('#tablelist').bootstrapTable("refresh", {query: {task_name: task_name, offset: 0, limit: limit}});
    });

    var service_id = $("#service_id").val();
    if (service_id != "") {
        var sel = $("#task_type").find('option[sid="' + service_id + '"]');
        sel.attr("selected", true);
        $("#form_condition_" + sel.attr("value")).show();
    }
    //任务类型事件
    $("#task_type").change(function () {
        $(".task-condition").hide();
        $(".task-condition")[0].reset();
        var value = $(this).val();
        if (value != "") {
            $("#form_condition_" + value).show();
        }
    });

    //创建任务
    $("#btn_task_create").click(function () {
        save();
    });

    function save() {
        $("#btn_task_create").unbind("click");
        var task_name = $("#task_name").val();
        var task_type = $("#task_type").val();
        if (task_name == "") {
            layer.msg("请填写任务名称！");
            $("#btn_task_create").bind("click", function () {
                save();
            });
            return;
        }
        if (task_type == "") {
            layer.msg("请选择任务类型！");
            $("#btn_task_create").bind("click", function () {
                save();
            });
            return;
        }
        if (task_type == "10000") {
            var keywords_10000 = $("#keywords_10000").val();
            var task_count_10000 = $("#task_count_10000").val();
            if (keywords_10000 == "") {
                layer.msg("请填写关键词！");
                $("#btn_task_create").bind("click", function () {
                    save();
                });
                return;
            }
            var keywords = keywords_10000.replace(/(^\s*)|(\s*$)/g, "");
            keywords = keywords.split('\n');
            if (keywords.length > 50) {
                layer.msg("关键词不得超过50个！");
                $("#btn_task_create").bind("click", function () {
                    save();
                });
                return;
            }
            if (task_count_10000 > 100) {
                layer.msg("最多查询前100名！");
                $("#btn_task_create").bind("click", function () {
                    save();
                });
                return;
            }
            $.post("/member/task/10000/save", {
                "task_name": task_name,
                "task_type": task_type,
                "keywords": keywords_10000,
                "task_count": task_count_10000
            }, function (data) {
                if (data.code == 200) {
                    layer.msg("创建任务成功！");
                    window.history.back();
                } else {
                    layer.alert(data.message, {"icon": 2});
                }
                $("#btn_task_create").bind("click", function () {
                    save();
                });
            }, "json");
        }
    }

    //任务结果
    var task_id = $("#task_id").val();
    if (task_id != "") {
        $('#task_result_10000').bootstrapTable({
            url: '/member/task/10000/' + task_id + '/list?_time=' + new Date().getTime(),
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
                        var pageSize = $('#task_result_10000').bootstrapTable('getOptions').pageSize;//通过表的#id 可以得到每页多少条
                        var pageNumber = $('#task_result_10000').bootstrapTable('getOptions').pageNumber;//通过表的#id 可以得到当前第几页
                        return pageSize * (pageNumber - 1) + index + 1
                    }
                }, {
                    field: 'keyword',
                    title: '关键词',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'rank',
                    title: '排名',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'site_url',
                    title: '网址',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'page_url',
                    title: '页面地址',
                    align: 'center',
                    valign: 'middle',
                    formatter: function (value, row, index) {
                        return '<div style="width: 600px;white-space:nowrap;overflow-x: auto;">' + value + '</div>'
                    }
                }, {
                    field: 'page_title',
                    title: '页面标题',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'weight',
                    title: '权重',
                    align: 'center',
                    valign: 'middle'
                }, {
                    field: 'top100',
                    title: 'top100',
                    align: 'center',
                    valign: 'middle'
                }],
        });
    }
});

function delete_task(task_id) {
    layer.confirm('确定要删除吗？', {
        btn: ['是', '否'] //按钮
    }, function () {
        $.post('/member/task/' + task_id + '/delete', {}, function (data) {
            if (data.code == 200) {
                layer.msg("删除成功！");
                $('#tablelist').bootstrapTable("refresh");
            } else {
                layer.alert(data.message, {"icon": 2});
            }
        }, "json")
    });
}