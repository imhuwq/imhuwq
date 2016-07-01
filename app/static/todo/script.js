$(document).ready(function () {

    // Js in To-do home page
    if (window.location.pathname == $TODO_INDEX_PATH) {
        var task_input = $('#id-task-input');
        task_input.on("keypress", function (e) {
            if (e.which == 13) {
                var task_content = task_input.val().trim();
                var task_comp = task_content.match(/^@([0-1]{2})(.*)/);
                if (!task_comp) task_comp = ['', '00', task_content];
                var task_level = task_comp[1];
                var task_text = '';
                if (task_level) {
                    task_text = task_comp[2].trim();
                }
                else {
                    task_level = '00';
                    task_text = task_content
                }
                $.post($SCRIPT_ROOT + '/ajax-todo/new-task',
                    {
                        task_text: task_text,
                        task_level: task_level,
                        csrf_token: $CSRF_TOKEN
                    },
                    function (data) {
                        if (data.status == 200) {
                            var last_finished_task = $(".cls-task-finished.cls-task-" + task_level).eq(-1);
                            var last_unfinished_task = $(".cls-task-unfinished.cls-task-" + task_level).eq(-1);
                            var last_task = $(".cls-task-" + task_level).eq(-1);
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
                            if (last_task.prop('id') == (last_finished_task.prop('id'))) {
                                new_task.insertAfter(last_task.parent('del'))
                            }
                            else {
                                new_task.insertAfter(last_task)
                            }
                        }
                        else {
                            flash(data.message)
                        }
                    });
                task_input.val('')
            }

        });

        var task_list = $('#id-task-list');
        task_list.on("dblclick", ".cls-task", function () {
            $(this).css({
                'color': 'gray'
            });
            $(this).wrap('<del/>');
            this.className = this.className.replace('cls-task-unfinished', 'cls-task-finished');
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
                        flash(data.message)
                    }
                })
        });

        var clicking_task;
        var html_body = $("body");

        html_body.on('contextmenu', '.cls-task', (function (e) {

            $(".cls-task-menu").remove();

            var x = e.pageX + 30;
            var y = e.pageY - 20;

            clicking_task = $(this);

            var menu = $("<div/>", {
                class: "cls-task-menu",
                style: "position:absolute;left:" + x + "px;top:" + y + "px;"
            });

            var menu_items = $("<ul/>", {
                class: "cls-task-menu-items"
            }).appendTo(menu);

            var flow_task = $("<li/>", {
                class: "flow-task",
                html: "flow&nbsp;&nbsp; &raquo;"
            }).appendTo(menu_items);

            var arrange_task = $("<li/>", {
                class: "arrange-task",
                html: "优先&nbsp; &ReverseUpEquilibrium;"
            }).appendTo(menu_items);

            var delete_task = $("<li/>", {
                class: "cls-delete-task",
                html: "删除&nbsp; &times;"
            }).appendTo(menu_items);

            var create_project = $("<li/>", {
                class: "cls-create-project",
                html: "项目&nbsp; &rtriltri;"
            }).appendTo(menu_items);

            menu.appendTo("body");

            return false
        }));


        html_body.on("click", ".cls-delete-task", function () {
            var clicking_task_id = clicking_task.prop("id").match(/\d+/);

            $.post($SCRIPT_ROOT + '/ajax-todo/delete-task',
                {
                    id: parseInt(clicking_task_id),
                    csrf_token: $CSRF_TOKEN
                },
                function (data) {
                    if (data.status == 200) {
                        clicking_task.remove()
                    }
                    else {
                        flash(data.message)
                    }
                })
        });

        $("html").on("click", function () {
            $(".cls-task-menu").remove()
        });

    }


});

function flash(message) {
    var msg_box = $('#flashed-message');
    var msg = $('<div/>', {
        'class': 'alert alert-warning fade in',
        'id': 'flash',
        'html': message
    }).prependTo(msg_box);
    var btn = $('<button/>', {
        'type': 'button',
        'class': 'close',
        'data-dismiss': 'alert',
        'html': '&times;'
    }).appendTo(msg);
}