from flask import Blueprint, request, redirect, url_for, render_template, jsonify, abort, flash
from ..helpers import admin_required
from .. import db
from ..forms import PostForm, ProfileForm, SiteSettingForm, PasswordSetForm, CategoryForm
from ..models import Post, Tag, Category, Settings, User
from sqlalchemy import or_

admin = Blueprint('admin', __name__, )


@admin.route('/index')
@admin_required
def index():
    posts_count = Post.query.filter_by(type='article').count()
    tags_count = Tag.query.count()
    cates_count = Category.query.count()
    sets = Settings.query.get(1)
    user = User.query.get(1)
    return render_template('admin/index.html', title='后台',
                           posts_count=posts_count, tags_count=tags_count,
                           cates_count=cates_count, sets=sets, user=user)


@admin.route('/site')
@admin_required
def site():
    form = SiteSettingForm()
    sets = Settings.query.get(1)
    if form.validate_on_submit():
        sets.site_title = form.title.data
        sets.site_description = form.descp.data
        return redirect(url_for('admin.site'))
    form.title.data = sets.site_title
    form.descp.data = sets.site_description
    return render_template('admin/site.html',
                           form=form,
                           sets=sets,
                           title='站点设置')


@admin.route('/blog')
@admin_required
def blog():
    posts_count = Post.query.filter_by(type='article').count()
    cates_count = Category.query.count()
    tags_count = Tag.query.count()
    sets = Settings.query.get(1)
    return render_template('admin/blog.html',
                           title='博客管理',
                           sets=sets,
                           posts_count=posts_count,
                           cates_count=cates_count,
                           tags_count=tags_count)


# below is about user account
@admin.route('/profile')
@admin_required
def profile():
    form = ProfileForm()
    user = User.query.get(1)
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        return redirect(url_for('admin.index'))
    form.name.data = user.name
    form.email.data = user.email
    return render_template('admin/profile.html',
                           form=form,
                           title='个人资料')


@admin.route('/profile/password', methods=['GET', 'POST'])
@admin_required
def password():
    form = PasswordSetForm()
    if form.validate_on_submit():
        user = User.query.get(1)
        if user.verify_password(form.old.data):
            user.password = form.new.data
            return redirect(url_for('admin.index'))
        else:
            flash('旧密码不正确')
            return redirect(url_for('admin.change_password'))
    return render_template('admin/password.html',
                           title='更改密码',
                           form=form)


# below is about post
@admin.route('/blog/post', methods=['GET', 'POST'])
@admin_required
def new_post():
    form = PostForm()

    if form.validate_on_submit():
        p = Post(
            title=form.title.data,
            body=form.content.data,
            publicity=form.publicity.data,
            commendable=form.commendable.data
        )
        p.type = 'article' if form.publish.data else 'draft'
        db.session.add(p)

        try:
            category_id = request.form['category']
        except KeyError:
            category_id = 1
        cate = Category.query.get(category_id)
        if cate is None:
            cate = Category(id=1, name="默认分类")
            db.session.add(cate)
        p.category = cate
        p.tags = form.tags.data

        if form.save.data:
            return redirect(url_for('admin.edit_post', post_link=p.link, post_type="main"))
        elif form.publish.data:
            return redirect(url_for('blog.post', post_link=p.link, post_category_link=p.category_link))
    cates = Category.query.filter_by(parent_id=None).order_by(Category.order.asc()).all()
    return render_template("admin/new_post.html",
                           form=form,
                           title='书写文章',
                           categories=cates)


@admin.route('/blog/post/<path:post_link>/<post_type>', methods=['GET', 'POST'])
@admin_required
def edit_post(post_link, post_type):
    p = Post.query.filter_by(title=post_link).first()
    form = PostForm()
    form.post_id.data = p.id

    if p.main_id:
        abort(404)

    if post_type == "draft":
        p = p.draft
        if p is None:
            return redirect(url_for('admin.edit_post', post_link=p.link, post_type='main'))
    elif post_type != "main":
        return redirect(url_for("admin.edit_post", post_link=p.link, post_type="main"))

    if form.validate_on_submit():
        try:
            category_id = request.form['category']
        except KeyError:
            category_id = 1
        new_cate = Category.query.get(category_id)
        if new_cate is None:
            new_cate = Category(id=1, name='默认分类')
            db.session.add(new_cate)

        if form.save.data:
            if post_type == 'main' and p.type == 'article':
                draft = p.draft
                if draft is None:
                    draft = Post(type='draft',
                                 main_id=p.id)
                    db.session.add(draft)
                    db.session.flush()
                post_type = 'draft'
            else:
                draft = p
            draft.category = new_cate
            draft.tags = form.tags.data

            draft.title = form.title.data
            draft.body = form.content.data
            draft.commendable = form.commendable.data
            draft.publicity = form.publicity.data
            return redirect(url_for('admin.edit_post', post_link=draft.link, post_type=post_type))

        elif form.publish.data:
            if p.type == 'draft' and p.main is not None:
                p_main = p.main
                db.session.delete(p)
                p = p_main
            p.title = form.title.data
            p.body = form.content.data
            p.publicity = form.publicity.data
            p.commendable = form.commendable.data
            p.type = 'article'
            p.category = new_cate
            p.tags = form.tags.data
            return redirect(url_for('blog.post', post_link=p.link, post_category_link=p.category_link))

    form.title.data = p.title
    form.content.data = p.body
    form.tags.data = p.tags
    form.commendable.data = p.commendable
    form.publicity.data = p.publicity
    cates = Category.query.filter_by(parent_id=None).order_by(Category.order.asc()).all()
    return render_template("admin/new_post.html",
                           form=form, post=p,
                           categories=cates,
                           title="编辑文章")


@admin.route('/blog/posts', methods=['GET', 'POST'])
@admin_required
def manage_posts():
    category = request.args.get('category')
    status = request.args.get('status')
    publicity = request.args.get('publicity')
    commendable = request.args.get('commendable')
    tag = request.args.get('tag')
    query = Post.query.filter_by(main_id=None)
    if category:
        category = Category.query.filter_by(name=category).first()
        if category:
            query = query.filter(or_(Post.category_link.like(category.link),
                                     Post.category_link.like(category.link + '/%')))
    if tag:
        if tag == ',':
            query = query.filter(or_((Post.tags_name == ''),
                                     Post.tags_name is None))
        else:
            query = query.filter(or_(Post.tags_name.like(tag + '、%'),
                                     Post.tags_name.like('%、' + tag),
                                     Post.tags_name.like(tag),
                                     Post.tags_name.like('%、' + tag + '、%')))
    if publicity:
        if publicity == 'True':
            query = query.filter_by(publicity=True)
        elif publicity == 'False':
            query = query.filter_by(publicity=False)
    if commendable:
        if commendable == 'On':
            query = query.filter_by(commendable=True)
        elif commendable == 'Off':
            query = query.filter_by(commendable=False)
    if status:
        if status == 'Article':
            query = query.filter_by(type='article', draft=None)
        elif status == 'Draft':
            query = query.filter_by(type='draft')
        elif status == 'Saved':
            query = query.filter(Post.draft != None)

    query = query.order_by(Post.date.desc())
    if query.count() <= 10:
        posts = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, error_out=False, per_page=10
        )
        posts = pagination.items
    categories = Category.query.filter_by(parent_id=None).all()
    tags = Tag.query.all()
    return render_template('admin/post.html',
                           title='管理文章',
                           posts=posts, tags=tags,
                           categories=categories,
                           pagination=pagination,
                           )


# below is about comment
@admin.route('/blog/comment', methods=['GET', 'POST'])
@admin_required
def manage_comment():
    sets = Settings.query.get(1)
    sets.enable_post_comment = not sets.enable_post_comment
    return redirect(url_for('admin.blog'))


# below is about category
@admin.route('/blog/new-category', methods=['GET', 'POST'])
@admin_required
def new_category():
    form = CategoryForm()
    if form.validate_on_submit():
        if '/' in form.name.data:
            flash('分类名中不能包含"/"')
            return redirect(url_for('admin.new_category'))
        name = form.name.data
        order = form.order.data
        try:
            parent_id = request.form.get('parent')
            parent = Category.query.get(parent_id)
        except KeyError:
            parent = None
        cate = Category(name=name, order=order)
        db.session.add(cate)
        cate.be_child_of(parent)
        return redirect(url_for('admin.manage_categories'))
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('admin/new_category.html',
                           title='新建分类',
                           form=form,
                           categories=categories)


@admin.route('/blog/edit-category/<path:category_link>', methods=['GET', 'POST'])
@admin_required
def edit_category(category_link):
    form = CategoryForm()
    cate = Category.query.filter_by(link=category_link).first()
    if form.validate_on_submit():
        if '/' in form.name.data:
            flash('分类名中不能包含"/"')
            return redirect(url_for('admin.new_category'))
        name = form.name.data
        order = form.order.data
        try:
            parent_id = request.form.get('parent')
            parent = Category.query.get(parent_id)
        except KeyError:
            parent = None
        cate.name = name
        cate.order = order
        cate.be_child_of(parent)
        if parent:
            return redirect(url_for('admin.manage_category', category_link=cate.parent.link))
        else:
            return redirect(url_for('admin.manage_categories'))
    form.name.data = cate.name
    form.order.data = cate.order
    categories = Category.query.filter_by(parent_id=None).all()
    return render_template('admin/new_category.html',
                           title='编辑分类',
                           form=form,
                           category=cate,
                           categories=categories)


@admin.route('/blog/category', methods=['GET', 'POST'])
@admin_required
def manage_categories():
    categories = Category.query.filter_by(parent_id=None).order_by(Category.order.asc()).all()
    return render_template('admin/category.html',
                           title='管理分类',
                           categories=categories)


@admin.route('/blog/category/<path:category_link>', methods=['GET', 'POST'])
@admin_required
def manage_category(category_link):
    category = Category.query.filter_by(link=category_link).first()
    categories = Category.query.filter_by(parent_id=category.id).order_by(Category.order.asc()).all()
    return render_template('admin/category.html',
                           title='管理分类',
                           category=category,
                           categories=categories)


# below is about tag
@admin.route('/blog/tag', methods=['GET', 'POST'])
@admin_required
def manage_tags():
    query = Tag.query
    if query.count() <= 15:
        tags = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, int)
        pagination = query.paginate(page=page, per_page=15, error_out=False)
        tags = pagination.items
    return render_template('admin/tag.html',
                           title='管理标签',
                           pagination=pagination,
                           tags=tags)


@admin.route('/blog/tag/<path:tag_name>')
@admin_required
def edit_tag(tag_name):
    tag = Tag.query.filter_by(name=tag_name).first()
    return ''
