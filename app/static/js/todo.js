$(document).ready(function () {

    // Js in To-do home page
    if (window.location.pathname == $TODO_INDEX_PATH) {
        var task_input = $('#id-task-input');
        task_input.on("keypress", function (e) {
            if (e.which == 13) {

                var task_content = task_input.val().trim();
                // the regex matches an standard input
                var task_comp = task_content.match(/^@([0-1]{2})(\s.*)/);
                // if the input is not standard, standardize it
                if (!task_comp) task_comp = ['', '00', task_content];

                var task_level = task_comp[1];
                var task_text = task_comp[2].trim();

                $.post($SCRIPT_ROOT + '/ajax-todo/new-task',
                    {
                        task_text: task_text,
                        task_level: task_level,
                        csrf_token: $CSRF_TOKEN
                    },
                    function (data) {
                        if (data.status == 200) {
                            var new_task = create_task_list(task_text, data.id, task_level);
                            insert_as_last_task_of_level(new_task, task_level);
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

            var x = e.pageX + 10;
            var y = e.pageY - 10;

            clicking_task = $(this);

            var menu = $("<div/>", {
                class: "cls-task-menu",
                style: "position:absolute;left:" + x + "px;top:" + y + "px;"
            });

            var menu_items = $("<ul/>", {
                class: "cls-task-menu-items"
            }).appendTo(menu);

            var flow_task = $("<li/>", {
                class: "cls-task-flow",
                html: "flow&nbsp;&nbsp; &raquo;"
            }).appendTo(menu_items);

            var arrange_task = $("<li/>", {
                class: "cls-task-priority",
                html: "优先&nbsp; &setmn;"
            }).appendTo(menu_items);

            var delete_task = $("<li/>", {
                class: "cls-task-delete",
                html: "删除&nbsp; &times;"
            }).appendTo(menu_items);

            var create_project = $("<li/>", {
                class: "cls-task-project",
                html: "项目&nbsp; &dollar;"
            }).appendTo(menu_items);

            var edit_task = $("<li/>", {
                class: "cls-task-edit cls-menu-bottom",
                html: "编辑&nbsp; &laquo;"
            }).appendTo(menu_items);

            menu.appendTo("body");

            return false
        }));

        html_body.on("click", ".cls-task-priority", function () {
            var clicking_task_id = clicking_task.prop("id").match(/\d+/);
            var clicking_task_level = clicking_task.prop("class").match(/.*-(\w+)/)[1];
            var new_level = prompt("新优先级");
            var new_class = clicking_task.prop("class").replace(/(.*-)\w+/, '$1' + new_level);

            $.post($SCRIPT_ROOT + '/ajax-todo/arrange-task',
                {
                    id: parseInt(clicking_task_id),
                    level: new_level,
                    csrf_token: $CSRF_TOKEN
                }, function (data) {
                    if (data.status == 200) {
                        var new_task = clicking_task.clone(true);
                        new_task.prop("class", new_class);
                        if (clicking_task.parent().prop('tagName') == 'DEL') {
                            new_task = $("<del/>").append(new_task)
                        }
                        clicking_task.remove();
                        insert_as_last_task_of_level(new_task, new_level);
                        update_task_order(clicking_task_level)

                    }
                    else {
                        flash(data.message)
                    }
                })
        });

        html_body.on("click", ".cls-task-delete", function () {
            var clicking_task_id = clicking_task.prop("id").match(/\d+/);
            var clicking_task_level = clicking_task.prop("class").match(/.*-(\w+)/)[1];

            $.post($SCRIPT_ROOT + '/ajax-todo/delete-task',
                {
                    id: parseInt(clicking_task_id),
                    csrf_token: $CSRF_TOKEN
                },
                function (data) {
                    if (data.status == 200) {
                        clicking_task.remove();
                        update_task_order(clicking_task_level)
                    }
                    else {
                        flash(data.message)
                    }
                })
        });

        html_body.on("click", ".cls-task-edit", function () {
            var clicking_task_id = clicking_task.prop("id").match(/\d+/);
            var clicking_task_level = clicking_task.prop("class").match(/.*-(\w+)/)[1];
            var clicking_task_text = clicking_task.get(0).lastChild.nodeValue.replace(/[\n:]/, '').trim();

            var task_content = prompt("请输入新任务", "@" + clicking_task_level + " " + clicking_task_text);
            // the regex matches an standard input
            var task_comp = task_content.match(/^@([0-1]{2})(\s.*)/);
            // if the input is not standard, standardize it
            if (!task_comp) task_comp = ['', '00', task_content];

            var task_level = task_comp[1];
            var task_text = task_comp[2].trim();

            $.post($SCRIPT_ROOT + '/ajax-todo/edit-task',
                {
                    id: parseInt(clicking_task_id),
                    level: task_level,
                    text: task_text,
                    csrf_token: $CSRF_TOKEN
                },
                function (data) {
                    if (data.status == 200) {
                        if (task_level == clicking_task_level) {
                            clicking_task.get(0).lastChild.nodeValue = ": " + task_text
                        }
                        else {

                            var new_task = create_task_list(task_text, clicking_task_id, task_level);
                            if (clicking_task.parent().prop('tagName') == 'DEL') {
                                new_task = $("<del/>").append(new_task)
                            }
                            clicking_task.remove();
                            insert_as_last_task_of_level(new_task, task_level);
                            update_task_order(clicking_task_level)
                        }
                    }
                    else {
                        flash(data.message)
                    }
                })

        });

        $("html").on("click", function () {
            $(".cls-task-menu").remove();
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

function insert_as_last_task_of_level(ele, level) {
    var last_finished_task = $(".cls-task-finished.cls-task-" + level).eq(-1);
    var last_task = $(".cls-task-" + level).eq(-1);
    var task_order = last_task.children(".cls-task-order").text();
    task_order = parseInt(task_order) + 1;
    ele.find(".cls-task-order").html(task_order);
    if (last_task.prop('id') == (last_finished_task.prop('id'))) {
        ele.insertAfter(last_task.parent('del'))
    }
    else {
        ele.insertAfter(last_task)
    }
}

function create_task_list(text, id, level, order) {
    order = order || 0;
    var new_task = $('<li/>', {
        class: "cls-task cls-task-unfinished cls-task-" + level,
        id: "id-task-" + id,
        text: ": " + text
    });
    $("<span/>", {
        class: "cls-task-order",
        text: order
    }).prependTo(new_task);
    return new_task
}

function update_task_order(level) {
    var targets = $('.cls-task-' + level);
    targets.each(function (index) {
        $(this).children(".cls-task-order").html(index);
    })
}