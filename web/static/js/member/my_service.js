$(function () {
    var service_id = $("#service_id").val();
    $('#consumelist').bootstrapTable({
        url: "/member/service/consume_log/" + service_id + "/list",
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
                    var pageSize = $('#consumelist').bootstrapTable('getOptions').pageSize;//通过表的#id 可以得到每页多少条
                    var pageNumber = $('#consumelist').bootstrapTable('getOptions').pageNumber;//通过表的#id 可以得到当前第几页
                    return pageSize * (pageNumber - 1) + index + 1
                }
            }, {
                field: 'consume_times',
                title: '消费次数',
                align: 'center',
                valign: 'middle',
                formatter: function (value, row, index) {
                    if (value > 0) {
                        return "+" + value;
                    }
                    return value;
                }
            }, {
                field: 'before_consume_times',
                title: '消费前次数',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'after_consume_times',
                title: '消费后次数',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'consume_reason',
                title: '消费原因',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'task_id',
                title: '任务id',
                align: 'center',
                valign: 'middle'
            }, {
                field: 'created_time',
                title: '创建时间',
                align: 'center',
                valign: 'middle'
            }],
    });
});
