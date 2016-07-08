from flask import Blueprint, request, redirect, url_for, render_template, current_app, abort
from flask_login import current_user
from ..models import Post, Category, Tag

blog = Blueprint('blog', __name__)


@blog.route('/index')
@blog.route('/')
def index():
    title = '博客'
    base_query = Post.query.filter_by(_type="article")
    base_query = base_query.filter_by(_public=True) if not current_user.is_administrator else base_query
    query = base_query.order_by(Post._publish_date.desc())

    if query.count() <= current_app.config['POSTS_PER_PAGE']:
        posts = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
        posts = pagination.items
    return render_template('blog/index.html',
                           title=title,
                           posts=posts,
                           pagination=pagination)


@blog.route('/post/<path:post_link>')
@blog.route('/category/<path:post_category_link>')
@blog.route('/tag/<path:post_tag_link>')
@blog.route('/archive/<path:post_date_link>')
def post(post_link=None, post_category_link=None, post_tag_link=None, post_date_link=None):
    not_found = True
    if post_link:
        p = Post.query.filter_by(_link=post_link).first()
        if p:
            not_found = False
    elif post_category_link:
        *category_link, post_link = post_category_link.split('/')
        category_link = '/'.join(category_link)
        p = Post.query.filter_by(_link=post_link).first()
        if p and category_link == p._category:
            not_found = False
    elif post_tag_link:
        *tag_link, post_link = post_tag_link.split('/')
        tag_link = '/'.join(tag_link)
        p = Post.query.filter_by(_link=post_link).first()
        if p and tag_link in [t.replace(' ', '_') for t in p.tags]:
            not_found = False
    elif post_date_link:
        *date, post_link = post_date_link.split('/')
        p = Post.query.filter_by(_link=post_link).first()
        if p and '/'.join(date) == '%s/%s' % (p.date.year, p.date.month):
            not_found = False

    if not_found:
        abort(404)

    return render_template('blog/single.html',
                           title=p.title,
                           posts=[p])


@blog.route('/categories')
def categories():
    cates = Category.query.filter_by(_level=0).filter(Category._posts_count != 0).order_by(Category._order).all()
    return render_template('blog/categories.html',
                           categories=cates,
                           title='分类',
                           cates=cates)


@blog.route('/categories/<path:category_link>')
def category(category_link):
    cate = Category.query.filter_by(_link=category_link).first()
    if not cate:
        abort(404)
    children = cate.children.all()
    base_query = Post.query.filter_by(_type="article")
    base_query = base_query.filter_by(_public=True) if not current_user.is_administrator else base_query
    query = base_query.order_by(Post._publish_date.desc())
    if query.count() <= current_app.config['POSTS_PER_PAGE']:
        ps = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
        ps = pagination.items
    cates = Category.query.filter_by(_level=0).filter(Category._posts_count != 0).order_by(Category._order).all()
    return render_template('blog/category.html',
                           category=cate,
                           categories=children,
                           posts=ps,
                           pagination=pagination,
                           title='分类:' + cate.name,
                           cates=cates)


@blog.route('/tags')
def tags():
    ts = Tag.query.filter(Tag._posts_count != 0).order_by(Tag._posts_count.desc()).all()
    return render_template('blog/tags.html',
                           tags=ts,
                           title='标签')


@blog.route('/tags/<path:tag_link>')
def tag(tag_link):
    t = Tag.query.filter_by(_link=tag_link).first()
    if not t:
        abort(404)
    base_query = Post.query.filter_by(_type="article")
    base_query = base_query.filter_by(_public=True) if not current_user.is_administrator else base_query
    query = base_query.order_by(Post._publish_date.desc())
    if query.count() <= current_app.config['POSTS_PER_PAGE']:
        ps = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
        ps = pagination.items

    tags = Tag.query.filter(Tag._posts_count != 0).order_by(Tag._posts_count.desc()).all()
    return render_template('blog/tag.html',
                           title='标签:' + tag_link,
                           pagination=pagination,
                           posts=ps,
                           tag=t,
                           tags=tags)


@blog.route('/archives')
def archive():
    title = '博客存档'
    ps = Post.query.filter_by(_type='article').order_by(Post._publish_date.desc()).all()
    return render_template('blog/archive.html',
                           posts=ps,
                           title=title,
                           )
