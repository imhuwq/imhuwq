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


@blog.route('/category/<path:post_category_link>/><post_title>')
@blog.route('/post/<post_title>', defaults={'post_category_link': None})
def post(post_title, post_category_link):
    p = Post.query.filter_by(title=post_title).first()
    if post_category_link != p.category_link:
        return redirect(url_for('blog.post', post_title=p.title, post_category_link=p.category_link))
    if p.publicity or current_user.is_administrator:
        cates = Category.query.filter_by(parent_id=None). \
            filter(Category.posts_count != 0). \
            order_by(Category.order).all()
        tags = Tag.query.filter(Tag.posts_count != 0).order_by(Tag.posts_count.desc()).all()
        return render_template('blog/single.html',
                               title=p.title,
                               posts=[p],
                               cates=cates,
                               tags=tags,
                               detailed=True)
    else:
        abort(404)


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
    cate = Category.query.filter_by(_link=category_link).first()
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


@blog.route('/tag/<tag_name>')
def tag(tag_name):
    tags = Tag.query
    t = tags.filter_by(name=tag_name).first()
    if not t:
        abort(404)
    query = Post.query.filter(or_(Post.tags_name.like(tag_name + '、%'),
                                  Post.tags_name.like('%、' + tag_name),
                                  Post.tags_name.like(tag_name),
                                  Post.tags_name.like('%、' + tag_name + '、%'))) \
        .order_by(Post.date.desc())
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
                           title='标签:' + tag_name,
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
