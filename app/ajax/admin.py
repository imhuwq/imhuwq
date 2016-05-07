from flask import Blueprint, request, flash, jsonify
from ..helpers import admin_required
from .. import db
from ..models import Post, Tag, Category

ajax_admin = Blueprint('ajax_admin', __name__, )


@ajax_admin.route('/new-category', methods=['GET', 'POST'])
@admin_required
def new_category():
    name = request.form.get('name').strip()
    parent_id = request.form.get('parent_id')
    if name and parent_id:
        parent = Category.query.get(parent_id)
        cate = Category.query.filter_by(_name=name).first()
        if cate is None:
            cate = Category(
                name=name
            )
            if parent:
                cate.be_child_of(parent)
            db.session.add(cate)
            db.session.commit()
            return jsonify({
                'action': 'add',
                'name': cate.name,
                'id': cate.id,
                'parent_id': cate.parent_id
            })
        else:
            return jsonify({
                'action': 'select',
                'id': cate.id
            })


@ajax_admin.route('/new-tag', methods=['GET', 'POST'])
@admin_required
def new_tag():
    data = request.form.get('new_tags')
    if data:
        tags_name = data.strip().split('、')
        for name in tags_name:
            t = Tag.query.filter_by(name=name).first()
            if t is None:
                t = Tag(name=name)
                db.session.add(t)
                db.session.commit()
    return ''


@ajax_admin.route('/delete-post', methods=['GET', 'POST'])
@admin_required
def delete_post():
    post_id = request.form.get('post_id')
    if post_id:
        post = Post.query.get_or_404(post_id)
        db.session.delete(post)
    return ''


@ajax_admin.route('/change-post-publicity', methods=['GET', 'POST'])
@admin_required
def change_post_publicity():
    post_id = request.form.get('post_id')
    publicity = request.form.get('publicity')
    if post_id and publicity:
        post = Post.query.get_or_404(post_id)
        post.publicity = int(publicity.strip())
    return ''


@ajax_admin.route('/change-post-commendable', methods=['GET', 'POST'])
@admin_required
def change_post_commendable():
    post_id = request.form.get('post_id')
    commendable = request.form.get('commendable')
    if post_id and commendable:
        post = Post.query.get_or_404(post_id)
        post.commendable = int(commendable.strip())
    return ''


@ajax_admin.route('/delete-all-selected-posts', methods=['GET', 'POST'])
@admin_required
def delete_all_selected_posts():
    posts_list = request.form.get('selected_posts').split(',')
    if posts_list:
        for post_id in posts_list:
            post = Post.query.filter_by(id=post_id).first()
            db.session.delete(post) if post else ''
    return ''


@ajax_admin.route('/set-posts', methods=['GET', 'POST'])
@admin_required
def set_posts():
    post_list = request.form.get('selected_posts').split(',')
    prop = request.form.get('property').strip()
    value = request.form.get('operation')
    if post_list and prop and value:
        for post_id in post_list:
            post = Post.query.filter_by(id=post_id).first()
            if prop == 'publicity':
                post.publicity = int(value)
            elif prop == 'comment':
                post.commendable = int(value)
    return ''


@ajax_admin.route('/update-posts-tag', methods=['GET', 'POST'])
@admin_required
def update_posts_tag():
    post_list = request.form.get('posts').split(',')
    operation = request.form.get('operation').strip()
    tags_list = request.form.get('tags').split(',')

    if post_list and operation and tags_list:
        for post_id in post_list:
            post = Post.query.get(post_id)
            old_tags = post.tags.split('、') if post.tags else []
            if post:
                if operation == 'reset':
                    new_tags = '、'.join(tags_list)
                elif operation == 'delete':
                    new_tags = '、'.join([tag for tag in old_tags if tag not in tags_list])
                elif operation == 'add':
                    add_tags = [tag for tag in tags_list if tag not in old_tags]
                    old_tags.extend(add_tags)
                    new_tags = '、'.join(old_tags)
                post.tags = new_tags
    return ''


@ajax_admin.route('/update-posts-cate', methods=['GET', 'POST'])
@admin_required
def update_posts_category():
    posts = request.form.get('posts').split(',')
    category = request.form.get('category')
    if posts and category:
        if category == '默认分类':
            cate = Category.query.get(1)
            if not cate:
                cate = Category(_name='默认分类')
                db.session.add(cate)
        else:
            cate = Category.query.filter_by(_name=category).first()
            if not cate:
                cate = Category(name=category)
                db.session.add(cate)
        for post in posts:
            p = Post.query.get(post)
            if p:
                p.category = cate
    return ''


@ajax_admin.route('/delete-all-selected-cates', methods=['GET', 'POST'])
@admin_required
def delete_all_selected_cates():
    cates_list = request.form.get('selected_cates').split(',')
    if '1' in cates_list:
        return jsonify({'warning': '默认分类无法被删除'})
    else:
        for cate_id in cates_list:
            cate = Category.query.get(cate_id)
            cate.delete_category()
    return ''


@ajax_admin.route('/delete-cate', methods=['GET', 'POST'])
@admin_required
def delete_category():
    cate_id = request.form.get('cate_id')
    cate = Category.query.filter_by(id=cate_id).first()
    if cate.id != 1:
        cate.delete_category()
        return jsonify({'success': 'action completed'})
    return jsonify({'warning': 'category not found'})


@ajax_admin.route('/merge-all-selected-cates', methods=['GET', 'POST'])
@admin_required
def merge_all_selected_cates():
    selected_cates = request.form.get('selected_cates').split(',')
    new_cate_name = request.form.get('new_cate_name')
    Category.marge(new_cate_name, selected_cates)
    return ''


@ajax_admin.route('/add-tag', methods=['GET', 'POST'])
@admin_required
def add_tag():
    tags_name = request.form.get('tags_name').split(',')
    for name in tags_name:
        tag = Tag.query.filter_by(name=name).first()
        if tag is None:
            tag = Tag(name=name)
            db.session.add(tag)
    return ''


@ajax_admin.route('/delete-tag', methods=['GET', 'POST'])
@admin_required
def delete_tag():
    tag_id = request.form.get('tag_id')
    tag = Tag.query.filter_by(id=tag_id).first()
    if tag:
        tag.delete_tag()
    return ''


@ajax_admin.route('/delete-all-selected-tags', methods=['GET', 'POST'])
@admin_required
def delete_all_selected_tags():
    tags_list = request.form.get('selected_tags').split(',')
    for tag in tags_list:
        t = Tag.query.get(tag)
        t.delete_tag()
    return ''


@ajax_admin.route('/merge-all-selected-tags', methods=['GET', 'POST'])
@admin_required
def merge_all_selected_tags():
    selected_tags = request.form.get('selected_tags').split(',')
    new_tag_name = request.form.get('new_tag_name')
    Tag.merge(new_tag_name, selected_tags)
    return ''

