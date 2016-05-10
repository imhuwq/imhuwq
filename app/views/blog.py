from flask import Blueprint, request, redirect, url_for, render_template, current_app, abort
from flask.ext.login import current_user
from ..models import Post, Category, Tag
from sqlalchemy import or_

blog = Blueprint('blog', __name__)


@blog.route('/index')
def index():
    title = '博客'
    query = Post.query.filter_by(type="article").order_by(Post.date.desc())
    if query.count() <= current_app.config['POSTS_PER_PAGE']:
        posts = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
        posts = pagination.items
    cates = Category.query.filter_by(parent_id=None).filter(Category.posts_count != 0).order_by(Category.order).all()
    tags = Tag.query.filter(Tag.posts_count != 0).order_by(Tag.posts_count.desc()).all()
    return render_template('blog/index.html',
                           title=title,
                           posts=posts,
                           cates=cates,
                           tags=tags,
                           detailed=False,
                           pagination=pagination)


@blog.route('/post><path:post_link>')
@blog.route('/category/<path:post_category_link>><path:post_link>')
@blog.route('/tag/<path:tag_link>><path:post_link>')
@blog.route('/archive/<path:post_date>><path:post_link>')
def post(post_link, post_category_link=None, tag_link=None, post_date=None):
    p = Post.query.filter_by(link=post_link).first()
    if not p:
        abort(404)
    if not p.publicity and not current_user.is_administrator:
        abort(404)
    if post_category_link and post_category_link != p.category_link:
        abort(404)
    if tag_link:
        t = Tag.query.filter_by(link=tag_link).first()
        if t.name not in p.tags:
            abort(404)
    if post_date and post_date != '%s/%s' % (p.date.year, p.date.month):
        abort(404)

    cates = Category.query.filter_by(parent_id=None). \
        filter(Category.posts_count != 0). \
        order_by(Category.order).all()
    tags = Tag.query.filter(Tag.posts_count != 0).order_by(Tag.posts_count.desc()).all()
    return render_template('blog/single.html',
                           title=p.title,
                           posts=[p],
                           cates=cates,
                           tags=tags)


@blog.route('/category')
def categories():
    display = request.args.get('display')
    if display == 'detail':
        return redirect(url_for('blog.index'))
    cates = Category.query.filter_by(parent_id=None).filter(Category.posts_count != 0).order_by(Category.order).all()
    tags = Tag.query.filter(Tag.posts_count != 0).order_by(Tag.posts_count.desc()).all()
    return render_template('blog/categories.html',
                           categories=cates,
                           title='分类',
                           cates=cates,
                           tags=tags)


@blog.route('/category/<path:category_link>')
def category(category_link):
    cate = Category.query.filter_by(link=category_link).first()
    if not cate:
        abort(404)
    children = Category.query.filter_by(parent_id=cate.id).order_by(Category.order).all()
    query = Post.query.filter(or_(Post.category_link.like(category_link),
                                  Post.category_link.like(category_link + '/%'))) \
        .order_by(Post.date.desc())
    if query.count() <= current_app.config['POSTS_PER_PAGE']:
        ps = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
        ps = pagination.items
    cates = Category.query.filter_by(parent_id=None).filter(Category.posts_count != 0).order_by(Category.order).all()
    tags = Tag.query.filter(Tag.posts_count != 0).order_by(Tag.posts_count.desc()).all()
    return render_template('blog/category.html',
                           category=cate,
                           categories=children,
                           posts=ps,
                           pagination=pagination,
                           title='分类:' + cate.name,
                           cates=cates,
                           tags=tags)


@blog.route('/tag/<path:tag_link>')
def tag(tag_link):
    tags = Tag.query
    t = tags.filter_by(link=tag_link).first()
    if not t:
        abort(404)
    query = t.posts.order_by(Post.date.desc())
    if query.count() <= current_app.config['POSTS_PER_PAGE']:
        ps = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
        ps = pagination.items

    cates = Category.query.filter_by(parent_id=None).filter(Category.posts_count != 0).order_by(Category.order).all()
    tags = Tag.query.filter(Tag.posts_count != 0).order_by(Tag.posts_count.desc()).all()
    return render_template('blog/tag.html',
                           title='标签:' + tag_link,
                           pagination=pagination,
                           posts=ps,
                           tag=t,
                           cates=cates,
                           tags=tags)


@blog.route('/archive')
def archive():
    title = '博客存档'
    ps = Post.query.filter_by(type='article').order_by(Post.date.desc()).all()
    cates = Category.query.filter_by(parent_id=None).filter(Category.posts_count != 0).order_by(Category.order).all()
    tags = Tag.query.filter(Tag.posts_count != 0).order_by(Tag.posts_count.desc()).all()
    return render_template('blog/archive.html',
                           posts=ps,
                           title=title,
                           cates=cates,
                           tags=tags
                           )
