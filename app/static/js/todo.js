$(document).ready(function () {
    var html_body = $("body");
    // Js in To-do home page
    if (window.location.pathname == $TODO_INDEX_PATH ||
        window.location.pathname == '/' ||
        window.location.pathname == '/index') {
        var task_input = $('#id-task-input');
        task_input.on("keypress", function (e) {
            if (e.which == 13) {

                var task_content = task_input.val().trim();
                if (task_content == '') {
                    return false
                }
                var task = extract_task_input(task_content);

                $.post($SCRIPT_ROOT + '/ajax-todo/new-task',
                    {
                        task_text: task.text,
                        task_level: task.level,
                        csrf_token: $CSRF_TOKEN
                    },
                    function (data) {
                        if (data.status == 200) {
                            var new_task = create_task_list(task.text, data.id, task.level);
                            insert_as_last_task_of_level(new_task, task.level);
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

        html_body.on('contextmenu', '.cls-task', (function (e) {

            $(".cls-task-menu").remove();

            var x = e.pageX + 10;
            var y = e.pageY - 10;

            clicking_task = $(this);
            var clicking_task_level = clicking_task.prop("class").match(/.*-(\w+)/)[1];


            var menu = $("<div/>", {
                class: "cls-task-menu",
                style: "position:absolute;left:" + x + "px;top:" + y + "px;"
            });

            var menu_items = $("<ul/>", {
                class: "cls-task-menu-items"
            }).appendTo(menu);

            if (clicking_task_level == '11') {
                var flow_task = $("<li/>", {
                    class: "cls-task-flow",
                    html: "flow&nbsp;&nbsp; &raquo;"
                }).appendTo(menu_items);
            }

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

        html_body.on("click", ".cls-task-flow", function () {
            var clicking_task_id = clicking_task.prop("id").match(/\d+/);

            window.location.pathname = $SCRIPT_ROOT + '/todo/' + clicking_task_id + '/flow';

        });

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
                        move_task_to_new_level(clicking_task, new_task, clicking_task_level, new_level)
                    }
                    else {
                        flash(data.message)
                    }
                })
        });

        html_body.on("click", ".cls-task-delete", function () {
            if (confirm("删除这条Task")) {
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
            }


        });

        html_body.on("click", ".cls-task-edit", function () {
            var clicking_task_id = clicking_task.prop("id").match(/\d+/);
            var clicking_task_level = clicking_task.prop("class").match(/.*-(\w+)/)[1];

            var task_content = prompt("请输入新任务").trim();

            var task = extract_task_input(task_content);

            $.post($SCRIPT_ROOT + '/ajax-todo/edit-task',
                {
                    id: parseInt(clicking_task_id),
                    level: task.level,
                    text: task.text,
                    csrf_token: $CSRF_TOKEN
                },
                function (data) {
                    if (data.status == 200) {

                        // the task level is NOT changed, change the text directly
                        if (task.level == clicking_task_level) {
                            clicking_task.get(0).lastChild.nodeValue = ": " + task.text
                        }

                        // the task level is changed, create a new and insert it into the target level, remove the old
                        else {

                            // create a new, with the new task text, new level and the same task id
                            var new_task = create_task_list(task.text, clicking_task_id, task.level);

                            move_task_to_new_level(clicking_task, new_task, clicking_task_level, task.level)
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

    // Js in To-do flow page
    var flow_path_regex = new RegExp($TODO_INDEX_PATH + "\\w+\/flow");
    if (window.location.pathname.match(flow_path_regex)) {
        var task_id = window.location.pathname.match(/.*\/(\w+)\//)[1];
        var task_idea = $(".cls-task-idea");
        var task_idea_origin = $(".cls-task-idea-origin").text().trim();
        var task_idea_html = task_idea.html().trim();

        var idea_wrapper = $("<div/>", {class: "cls-idea-text-wrapper"});
        var idea_text = $("<textarea/>", {
            class: "cls-task-idea-text",
            type: "text",
            name: "idea",
            text: task_idea_origin,
            height: task_idea.height() -5
        }).appendTo(idea_wrapper);

        // post the task idea text when click outside the text area
        $(document).on("click", function (e) {
            var tmp_idea_text = $(".cls-task-idea-text");
            var tmp_text_wrapper = $(".cls-idea-text-wrapper");

            if (tmp_text_wrapper.html() && !$(e.target).is(".cls-task-idea-text")) {
                post_this_edit(tmp_text_wrapper, tmp_idea_text)
            }
            $(".cls-task-menu").remove();
        });

        task_idea.on("dblclick", function () {
            // double click to cancel the task idea edit when in editing
            var tmp_text_wrapper = $(".cls-idea-text-wrapper");
            if (tmp_text_wrapper.html()) {
                cancel_this_edit()
            }

            // double click to start edit
            else {
                task_idea.addClass("noselect");
                task_idea.css({
                    backgroundColor: "white",
                    border: "1px solid white"
                });
                task_idea.text('');
                idea_text.text(task_idea_origin);
                idea_wrapper.appendTo(task_idea);
                idea_text.focus()
            }

        });

        task_idea.on("keydown", function (e) {
            // cancel the task idea edit when press shift + enter
            if (e.shiftKey && e.which == 13) {
                cancel_this_edit()
            }

            // post the task idea text when press ctrl + enter
            else if (e.ctrlKey && e.which == 13) {
                var tmp_idea_text = $(".cls-task-idea-text");
                var tmp_text_wrapper = $(".cls-idea-text-wrapper");
                if (tmp_text_wrapper.html()) {
                    post_this_edit(tmp_text_wrapper, tmp_idea_text)
                }
            }
        });

        function post_this_edit(tmp_text_wrapper, tmp_idea_text) {
            if (tmp_idea_text.val().trim() == task_idea_origin) {
                task_idea.html(task_idea_html);
                task_idea.css({
                    backgroundColor: "rgb(235, 235, 235)",
                    border: "1px solid rgb(235, 235, 235)"
                });
            }
            else {
                $.post($SCRIPT_ROOT + '/ajax-todo/task-idea',
                    {
                        id: task_id,
                        idea: idea_text.val().trim(),
                        csrf_token: $CSRF_TOKEN
                    }, function (data) {
                        if (data.status == 200) {
                            task_idea.html(data.html);
                            task_idea_origin = data.idea;
                            task_idea_html = data.html;
                            task_idea.css({
                                backgroundColor: "rgb(235, 235, 235)",
                                border: "1px solid rgb(235, 235, 235)"
                            });
                            idea_text.height(task_idea.height() - 5)
                        }
                        else {
                            flash(data.message);
                            task_idea.html(task_idea_html);
                        }
                    });
            }
            task_idea.removeClass("noselect");
            tmp_text_wrapper.remove()

        }

        function cancel_this_edit() {
            var tmp_text_wrapper = $(".cls-idea-text-wrapper");
            if (tmp_text_wrapper.html()) {
                idea_text.val(task_idea_origin);
                task_idea.html(task_idea_html);
                task_idea.css({
                    backgroundColor: "rgb(235, 235, 235)",
                    border: "1px solid rgb(235, 235, 235)"
                });
                tmp_text_wrapper.remove();
                task_idea.removeClass("noselect");
            }
        }

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
    msg.delay(2000).fadeOut()
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

function extract_task_input(input) {
    var content = input.trim();

    // use the regex to match an standard input
    var task_comp = content.match(/^@([0-1]{2})(\s.*)/);
    // if the input is not standard, standardize it
    if (!task_comp) task_comp = ['', '00', content];

    return {
        "level": task_comp[1],
        "text": task_comp[2].trim()
    };

}

function move_task_to_new_level(old_task, new_task, old_level, new_level) {

    // if the old is finished, wrap the new with an del element
    if (old_task.parent().prop('tagName') == 'DEL') {
        new_task = $("<del/>").append(new_task)
    }

    // insert the new
    insert_as_last_task_of_level(new_task, new_level);

    // remove the old
    old_task.remove();
    update_task_order(old_level);

}
