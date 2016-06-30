$(document).ready(function () {

    // Js in To-do home page
    if (window.location.pathname == $TODO_INDEX_PATH) {
        var task_input = $('#id-task-input');
        task_input.on("keypress", function (e) {
            if (e.which == 13) {
                var task_comp = task_input.val().match(/^@([0-1]{2})(.*)/);
                var task_level = task_comp[1];
                var task_text = '';
                if (task_level) {
                    task_text = task_comp[2].trim();
                }
                else {
                    task_level = '00';
                    task_text = task_input.val().trim()
                }
                $.post($SCRIPT_ROOT + '/ajax-todo/new-task',
                    {
                        task_text: task_text,
                        task_level: task_level,
                        csrf_token: $CSRF_TOKEN
                    },
                    function (data) {
                        if (data.status == 200) {
                            var last_task = $(".cls-task-unfinished.cls-task-" + task_level).eq(-1);
                            var task_order = last_task.children(".cls-task-order").text();
                            task_order = parseInt(task_order) + 1;
                            var new_task = $('<li/>', {
                                class: "cls-task cls-task-unfinished cls-task-" + task_level,
                                id: "id-task-" + data.id,
                                text: ": " + task_text
                            });
                            $("<span/>", {
                                class: "cls-task-order",
                                text: task_order
                            }).prependTo(new_task);
                            new_task.insertAfter(last_task)
                        }
                        else {
                            alert('添加任务失败')
                        }
                    });
                task_input.val('')
            }

        });

        $('#id-task-list').on("dblclick", ".cls-task", function () {
            $(this).css({
                'color': 'gray'
            });
            $(this).wrap('<del/>');
            var task_id = $(this).attr('id').match(/\d+/);
            $.post($SCRIPT_ROOT + '/ajax-todo/finish-task',
                {
                    task_id: parseInt(task_id),
                    name: 'name',
                    csrf_token: $CSRF_TOKEN
                },
                function (data) {
                    if (data.status == 200) {

                    }
                    else {
                        alert('出现错误，操作可能没有成功')
                    }
                })
        })
    }


});