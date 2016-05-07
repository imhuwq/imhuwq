$(document).ready(function () {

    // Js works in post editor page
    if (window.location.pathname == ($ADMIN_NEW_POST_PATH) || $ADMIN_EDIT_POST_PATH) {
        // SELECT AND ADD CATEGORY IN POST EDITOR
        var existedCategories = [];
        $('.category-checkboxes').each(function () {
            existedCategories.push($(this).parent().text().trim())
        });

        var postEditorCateSelector = $('#post-editor-cate-selector');
        postEditorCateSelector.on('change', '.category-checkboxes', function () {
            $('.category-checkboxes').not(this).prop('checked', false);
        });

        // dynamically detect input and check if inputted category name is already existed
        //  if so, disable select parent category and scroll to and flash existed category
        var cate_input = $('#post-editor-cate-input');
        var cate_parent = $('#post-editor-cate-parent');
        cate_input.on('keyup paste', function () {
            if (existedCategories.indexOf(cate_input.val().trim()) > -1) {
                $('#post-editor-cate-parent').prop('disabled', true);
            }
            else {
                cate_parent.prop('disabled', false)
            }
        });

        // an ajax block to add new category flawlessly
        cate_input.on('keypress', function (e) {
            if (e.which == 13) {
                $('.category-checkboxes').prop('checked', false);
                if (cate_input.val().indexOf('/') > -1) {
                    flash('正在输入分类名称:' + cate_input.val() + ' 分类名中不能包含“/”')
                }
                else {
                    if (existedCategories.indexOf(cate_input.val()) > -1) {
                        var oldCate = $('#category-' + cate_input.val());
                        oldCate.children().first().prop('checked', true);
                        scrollIntoAndFlash(oldCate.parent(), oldCate);
                    }
                    else if (cate_input.val().trim() != '') {
                        $.post($SCRIPT_ROOT + '/ajax-admin/new-category', {
                            // the the name and parent id of the new category
                            name: cate_input.val().trim(),
                            parent_id: cate_parent.val()
                        }, function (data) {
                            // dealing with the html with the feedback data
                            // prepare for the adding and scrolling and flashing
                            var cateId = '#category' + data.id;
                            var selector = postEditorCateSelector;
                            var li = $('<li/>', {
                                class: 'list-group-item'
                            });
                            var span = $('<span/>', {
                                id: 'category-' + data.name,
                                text: data.name
                            }).prependTo(li);
                            $('<input/>', {
                                type: 'checkbox',
                                checked: true,
                                name: 'category',
                                value: data.id,
                                id: 'category' + data.id,
                                class: 'category-checkboxes'
                            }).prependTo(span);
                            $('<ul/>', {
                                class: 'list=group'
                            }).appendTo(li);
                            var position; // anchor to add html and to scroll to
                            var target; // target to flash
                            if (data.parent_id == null) {
                                selector.prepend(li);
                                existedCategories.push(data.name.trim());
                                target = selector.children().first();
                                scrollIntoAndFlash(target, target);
                            }
                            else {
                                // the parent category span, whose sibling is the children ul
                                position = $('#category' + data.parent_id).parent();
                                // add the new child category as a li under the children ul
                                position.siblings(1).prepend(li);
                                existedCategories.push(data.name.trim());
                                // the new category
                                target = position.siblings(1).children().first();
                                // scroll to the parent category and flash the new category
                                scrollIntoAndFlash(position, target);
                            }
                        });
                    }
                }
                cate_input.prop('value', null);
                $('#post-editor-cate-parent').prop('value', '-1');
                return false
            }
        });

        // style the parent selector of creating new category
        cate_parent.on('change', function () {
            if ($(this).val() == '-1') {
                $(this).addClass('option-placeholder');
                $('#no-parent').text('父分类...')
            }
            else {
                $(this).removeClass('option-placeholder');
                $('#no-parent').text('...')
            }
        });
        cate_parent.change();

        // prevent submit post editor form from pressing enter key
        var postEditorForm = $('#post-editor-title');
        postEditorForm.on('keypress', function (e) {
            return e.which !== 13;
        });


        // ADD TAG IN POST EDITOR
        var tagInput = $('#post-editor-tag-input');
        var tagSubmit = $('#tags');
        var preview = $('#post-editor-tag-preview');
        var fnlTags = [];
        tagSubmit.val().split(/,+/).forEach(function (item) {
            if (item.trim() != '') {
                fnlTags.push(item.trim())
            }
        });
        tagInput.on('keypress', function (e) {
            if ((e.which == 13) && (tagInput.val() != '')) {
                var newTags = '';
                tagInput.val().split(/,+|，+|、+/).forEach(function (item) {
                    if ((item.trim() != '') && (fnlTags.indexOf(item.trim()) < 0)) {
                        if (newTags == '') {
                            newTags = item.trim();
                        }
                        else {
                            newTags = newTags + '、' + item.trim();
                        }
                        fnlTags.push(item.trim());
                        var tag = $('<span/>', {
                            html: item.trim(),
                            class: 'tag-preview'
                        }).appendTo(preview);
                        $('<a/>', {
                            html: '&times;',
                            class: 'delete-tag-icon btn',
                            title: '删除'
                        }).appendTo(tag);
                    }
                });
                tagInput.prop('value', '');
                if (newTags != '') {
                    $.post($SCRIPT_ROOT + '/ajax-admin/new-tag', {new_tags: newTags});
                }
                tagSubmit.prop('value', fnlTags);
                return false
            }
        });

        // delete tag from tags list
        $('#post-editor-tag').on('click', '.delete-tag-icon', function () {
            var removed_tag = $(this).parent();
            fnlTags = removeItem(fnlTags, removed_tag.clone().children().remove().end().text().trim());
            removed_tag.remove();
            tagSubmit.prop('value', fnlTags);
        });

    }

    // Js works in admin table page
    if (window.location.pathname == $ADMIN_MANAGE_POST_PATH ||
        window.location.pathname.indexOf($ADMIN_MANAGE_CATE_PATH) > -1 ||
        window.location.pathname.indexOf($ADMIN_MANAGE_TAG_PATH) > -1) {
        var existedItem = [];
        var selectedItem = [];
        var itemCheckboxes = $('.item-selector');
        var selectAllBtn = $('#select-all');
        selectAllBtn.on('click', function () {
            if (selectAllBtn.text() == '全选') {
                selectedItem = [];
                selectAllBtn.text('取消');
                itemCheckboxes.prop('checked', true);
                itemCheckboxes.each(function () {
                    selectedItem.push($(this).closest('tr').prop('id').trim())
                })
            }
            else {
                selectAllBtn.text('全选');
                itemCheckboxes.prop('checked', false);
                selectedItem = [];
            }
        });
        // get selected item id
        $("#manage-table").on('change', '.item-selector', function () {
            var itemId = $(this).closest('tr').prop('id').trim();
            if ($(this).prop('checked') == true) {
                selectedItem.push(itemId)
            }
            else {
                selectedItem = removeItem(selectedItem, itemId)
            }
            if (selectedItem == existedItem) {
                selectAllBtn.text('取消')
            }
            else {
                selectAllBtn.text('全选')
            }
        });

        var confirmedDelete = false;

        // deal with pagination redirection after deleting post
        function afterDeleteItem(postId) {
            var page = $('.pagination .active a').text().trim();
            postId = postId || -1;

            if (postId != -1) {
                existedItem = removeItem(existedItem, postId);
                if (existedItem.length == 0) goPage(page)
            }
            else goPage(page);

            function goPage(page) {
                if (page > 1) {
                    page -= 1;
                    var new_page = window.location.toString();
                    new_page = new_page.replace(/([&?])page=\w+/, '$1page=' + page);
                    window.location.replace(new_page);
                }
                else window.location.reload()
            }
        }

        // Js works in post manage page
        if (window.location.pathname == $ADMIN_MANAGE_POST_PATH) {
            $('.post-row').each(function () {
                existedItem.push($(this).prop('id').trim())
            });

            // delete all selected posts
            $('#delete-all-selected').on('click', function () {
                if (confirm('您确定删除这些文章吗？') && selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/delete-all-selected-posts',
                        {selected_posts: selectedItem.join()},
                        function () {
                            afterDeleteItem()
                        })
                }
                else {
                    window.location.reload()
                }
            });

            // set property on all selected posts
            var setPost = $('.set-post');
            setPost.on('click', function () {
                var property = $(this).attr('property').trim();
                var operation = $(this).attr('operation').trim();
                if (selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/set-posts',
                        {
                            selected_posts: selectedItem.join(),
                            property: property,
                            operation: operation
                        },
                        function () {
                            window.location.reload()
                        })
                }
                else {
                    alert('请选择要进行操作的文章')
                }

            });

            // selected posts get tagged by...
            $('.update-posts-tag').on('click', function () {
                var operation = $(this).attr('operation');
                var newTag = [];
                var tmpTag;
                if (operation == 'reset') {
                    tmpTag = prompt('请输入新的标签名称，用英文逗号(,)分隔');
                }
                else if (operation == 'add') {
                    tmpTag = prompt('请输入要添加的标签，用英文逗号(,)分隔');
                }
                else if (operation == 'delete') {
                    tmpTag = prompt('请输入要删除的标签, 用英文逗号(,)分隔')
                }
                tmpTag.split(/,+|，+|、+/).forEach(function (item) {
                    if (item.trim() != '') {
                        newTag.push(item.trim())
                    }
                });
                if (newTag.length > 0 && selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/update-posts-tag',
                        {
                            posts: selectedItem.join(),
                            tags: newTag.join(),
                            operation: operation
                        },
                        function () {
                            window.location.reload()
                        })
                }
                else if (newTag.length == 0) {
                    alert('请输入标签名称')
                }
                else if (selectedItem.length == 0) {
                    alert('请选择要添加标签的文章')
                }
            });

            // categorise all selected posts
            $('.update-post-cate').on('click', function () {
                var operation = $(this).attr('operation');
                var newCate = '';
                if (operation == 'default') {
                    if (confirm('确定删除所选文章的所有分类吗？\n(将会被划入默认分类中)')) {
                        newCate = '默认分类'
                    }
                }
                else {
                    newCate = prompt('请输入新分类的名称')
                }
                if (newCate != '' && selectedItem.length > 0) {
                    if (newCate.indexOf('/') > -1) {
                        flash('分类名中不能含有“/”')
                    }
                    else {
                        $.post($SCRIPT_ROOT + '/ajax-admin/update-posts-cate',
                            {
                                category: newCate,
                                posts: selectedItem.join()
                            },
                            function () {
                                location.reload()
                            })
                    }

                }
                else if (newCate == '') {
                    alert('请输入分类名称')
                }
                else if (selectedItem.length == 0) {
                    alert('请选择要进行操作的文章')
                }
            });

            // delete post
            confirmedDelete = false;
            $('.delete-post-icon').on('click', function () {
                var postRow = $(this).closest('tr');
                var postId = postRow.prop('id');
                if (confirmedDelete == false) {
                    if (confirm('你确定要删除这篇文章吗？')) {
                        $.post($SCRIPT_ROOT + '/ajax-admin/delete-post', {post_id: postId}, function () {
                            postRow.remove();
                            afterDeleteItem(postId);
                            confirmedDelete = true
                        })
                    }
                }
                else {
                    $.post($SCRIPT_ROOT + '/ajax-admin/delete-post', {post_id: postId}, function () {
                        postRow.remove();
                        afterDeleteItem(postId)
                    })
                }
            });

            // disable comment
            $('.commendable-post-icon').on('dblclick', function () {
                var postId = $(this).closest('tr').prop('id').trim();
                var commendable;
                $(this).fadeOut(0).fadeIn(800);
                if ($(this).prop('title') == '禁止评论') {
                    commendable = 1;
                    $(this).prop({
                        'title': '开放评论',
                        'style': 'color:green'
                    });
                    $(this).children('span').prop('class', 'glyphicon glyphicon-ok-circle')
                }
                else {
                    commendable = 0;
                    $(this).prop({
                        'title': '禁止评论',
                        'style': 'color:orange'
                    });
                    $(this).children('span').prop('class', 'glyphicon glyphicon-ban-circle')
                }
                $.post($SCRIPT_ROOT + '/ajax-admin/change-post-commendable', {
                    post_id: postId,
                    commendable: commendable
                }, function () {

                });
            });

            // change post publicity
            $('.public-post-icon').on('dblclick', function () {
                var postId = $(this).closest('tr').prop('id').trim();
                var publicity;
                $(this).fadeOut(0).fadeIn(800);
                if ($(this).prop('title') == '仅自己可见') {
                    publicity = 1;
                    $(this).prop({
                        'title': '所有人可见',
                        'style': 'color:green'
                    });
                    $(this).children('span').prop('class', 'glyphicon glyphicon-eye-open')
                }
                else {
                    publicity = 0;
                    $(this).prop({
                        'title': '仅自己可见',
                        'style': 'color:orange'
                    });
                    $(this).children('span').prop('class', 'glyphicon glyphicon-eye-close')
                }
                $.post($SCRIPT_ROOT + '/ajax-admin/change-post-publicity', {
                    post_id: postId,
                    publicity: publicity
                }, function () {

                });
            });


            // get current filter
            var current_query = location.search;
            var current_filter = current_query ?
                JSON.parse(
                    '{"' + location.search.replace(/\?/, "")
                        .replace(/&/g, '","')
                        .replace(/=/g, '":"')
                    + '"}',
                    function (key, value) {
                        return key === "" ? value : decodeURIComponent(value)
                    }) : {};
            // change filter bar according to applied filter
            var statusBar = $('#post-status').children('div').children('.dropdown-toggle').get(0).childNodes[0];
            var cateBar = $('#post-cate').children('div').children('.dropdown-toggle').get(0).childNodes[0];
            var tagBar = $('#post-tag').children('div').children('.dropdown-toggle').get(0).childNodes[0];
            var pubBar = $('#post-publicity').children('div').children('.dropdown-toggle').get(0).childNodes[0];
            var comtBar = $('#post-commendable').children('div').children('.dropdown-toggle').get(0).childNodes[0];
            if (current_filter['status']) statusBar.nodeValue = '状态:' + current_filter['status'];
            if (current_filter['category']) cateBar.nodeValue = '分类:' + current_filter['category'];
            if (current_filter['tag']) {
                tagBar.nodeValue = current_filter['tag'] == ',' ?
                    '无标签' :
                '标签:' + current_filter['tag'];
            }
            if (current_filter['publicity']) pubBar.nodeValue = '公开:' + current_filter['publicity'];
            if (current_filter['commendable']) comtBar.nodeValue = '评论:' + current_filter['commendable'];


            // apply filter
            var filter = $('.apply-filter');
            filter.on('mouseover', function () {
                if ($(this).parent('li').attr('class') == 'disabled') {
                    $(this).prop('style', 'cursor:not-allowed')
                }
            });
            filter.on('click', function () {
                if (($(this).parent('li').attr('class') != 'disabled')) {
                    var filter = $(this).attr('filter');
                    var by = $(this).attr('by');
                    var old_page = location.toString();
                    var new_page;

                    by == '' ? delete current_filter[filter] : current_filter[filter] = by;

                    if (current_filter['page']) current_filter['page'] = 1;

                    current_filter = '?' + $.param(current_filter);
                    if (current_query) {
                        new_page = current_filter == '?' ?
                            old_page.replace(current_query, '') :
                            old_page.replace(current_query, current_filter)
                    }
                    else {
                        new_page = current_filter == '?' ?
                            old_page :
                        old_page + current_filter;
                    }
                    location.replace(new_page);
                }
            });


        }

        // Js works in category manage page
        if (window.location.pathname.indexOf($ADMIN_MANAGE_CATE_PATH) > -1) {
            $('.cate-row').each(function () {
                existedItem.push($(this).prop('id').trim())
            });

            // delete all selected category
            $('#delete-all-selected').on('click', function () {
                if (confirm('您确定删除这些分类吗？\n该分类下的文章和子分类将被并入其父分类') && selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/delete-all-selected-cates',
                        {selected_cates: selectedItem.join()},
                        function (data) {
                            if (data['warning']) {
                                alert(data['warning'])
                            }
                        })
                }

                window.location.reload()

            });

            // merge all selected category
            $('#merge-all-selected').on('click', function () {
                var newCate = prompt('请输入合并后的分类名称');
                if (newCate.indexOf('/') > -1) {
                    alert('分类名中不能包含“/”')
                }
                else if (
                    confirm('您确定合并这些分类吗？\n所有分类下的文章和子分类将被并入新的分类')
                    && selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/merge-all-selected-cates',
                        {
                            selected_cates: selectedItem.join(),
                            new_cate_name: newCate
                        },
                        function (data) {
                            if (data['warning']) {
                                alert(data['warning'])
                            }
                        })
                }
                window.location.reload()
            });

            // delete category
            confirmedDelete = false;
            $('.delete-cate-icon').on('click', function () {
                var cateRow = $(this).closest('tr');
                var cateId = cateRow.prop('id');
                if (cateId == '1') {
                    alert('默认分类无法被删除');
                    return false
                }
                else {
                    if (confirmedDelete == false) {
                        if (confirm('你确定要删除这个分类吗？\n分类下的子分类和文章都将划入其父分类')) {
                            $.post($SCRIPT_ROOT + '/ajax-admin/delete-cate', {cate_id: cateId}, function () {
                                cateRow.remove();
                                afterDeleteItem(cateId);
                                confirmedDelete = true
                            })
                        }
                    }
                    else {
                        $.post($SCRIPT_ROOT + '/ajax-admin/delete-cate', {cate_id: cateId}, function () {
                            window.location.reload()
                        })
                    }
                }

            });
            
            // move all selected category
            $('#move-all-selected').on('click', function () {
                var newCate = prompt('要把所选分类移入哪个分类中？');
                if (newCate.indexOf('/') > -1) {
                    alert('分类名中不能包含“/”')
                }
                else if (
                    confirm('您确定移动这些分类吗？\n它们将成为被移入分类的子分类')
                    && selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/move-all-selected-cates',
                        {
                            selected_cates: selectedItem.join(),
                            target_cate_name: newCate
                        },
                        function (data) {
                            if (data['warning']) {
                                alert(data['warning'])
                            }
                        })
                }
                window.location.reload()
            });

        }

        // Js works in tag manage page
        if (window.location.pathname.indexOf($ADMIN_MANAGE_TAG_PATH) > -1) {
            // delete all selected tag
            $('#delete-all-selected').on('click', function () {
                if (confirm('您确定删除这些标签吗？') && selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/delete-all-selected-tags',
                        {selected_tags: selectedItem.join()},
                        function (data) {
                            if (data['warning']) {
                                alert(data['warning'])
                            }
                        })
                }

                window.location.reload()

            });

            // merge all selected tag
            $('#merge-all-selected').on('click', function () {
                var newTag = prompt('请输入合并后的标签名称');
                if (newTag.indexOf('、') > -1) {
                    alert('分类名中不能包含“、”')
                }
                else if (
                    confirm('您确定合并这些标签吗？')
                    && selectedItem.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/merge-all-selected-tags',
                        {
                            selected_tags: selectedItem.join(),
                            new_tag_name: newTag
                        },
                        function (data) {
                            if (data['warning']) {
                                alert(data['warning'])
                            }
                        })
                }
                window.location.reload()
            });

            // delete tag
            confirmedDelete = false;
            $('.delete-cate-icon').on('click', function () {
                var tagRow = $(this).closest('tr');
                var tagId = tagRow.prop('id');

                if (confirmedDelete == false) {
                    if (confirm('你确定要删除这个标签吗？')) {
                        $.post($SCRIPT_ROOT + '/ajax-admin/delete-tag', {tag_id: tagId}, function () {
                            tagRow.remove();
                            afterDeleteItem(tagId);
                            confirmedDelete = true
                        })
                    }
                }
                else {
                    $.post($SCRIPT_ROOT + '/ajax-admin/delete-tag', {tag_id: tagId}, function () {
                        window.location.reload()
                    })
                }

            });

            // add tag
            $('#add-new').on('click', function () {
                var newTags = prompt('请输入要添加的标签，用(,)或者(、)隔离');
                newTags = newTags.split(/,+|、+|，+/);
                newTags = removeItem(newTags, '');
                if (newTags.length > 0) {
                    $.post($SCRIPT_ROOT + '/ajax-admin/add-tag', {
                        tags_name: newTags.join()
                    }, function () {
                        window.location.reload()
                    })
                }
                else {
                    alert('请输入标签名')
                }
            })
        }
    }

    // Js works in blog categories page
    if (window.location.pathname.indexOf($BLOG_CATEGORY_PATH) > -1) {
        var childCategory = $('.child-category');
        childCategory.on('click', function () {
            window.location.replace($SCRIPT_ROOT + $(this).children('a').attr('href'))
        });

        childCategory.on('mouseover', function () {
            // $(this).prop('style', 'box-shadow: rgb(245, 245, 245) -1px -1px 5px;');
            $(this).children('a').prop('style', 'color:rgb(55,55,55);')
        });

        childCategory.on('mouseout', function () {
            // $(this).prop('style', 'box-shadow: none;');
            $(this).children('a').prop('style', 'color:dimgray')

        });
    }
    
});


// global functions
// a function scroll to the position and flash the target
// both position and target should be result of a selector
function scrollIntoAndFlash(position, target) {
    position.get(0).scrollIntoView();
    target.fadeIn(300).fadeOut(300).fadeIn(300).fadeOut(300).fadeIn(300);
}

// a function to remove an specific value from an array
function removeItem(array, value) {
    array = array.filter(function (elem) {
        return elem != value
    });
    return array
}


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