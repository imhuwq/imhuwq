from flask import Blueprint, current_app, request, flash
from flask import render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user
from ..models import Settings, User, Post, Category, Tag
from .. import db
from ..forms import SetupForm01, SetupForm02, LoginForm

main = Blueprint('main', __name__)


@main.before_app_first_request
def before_app_first_request():
    db.create_all()
    sets = Settings.query.first()
    if sets is None:
        sets = Settings(site_initiated=False,
                        site_admin_email=current_app.config['SITE_ADMIN_EMAIL'])
        db.session.add(sets)
    cate = Category.query.get(1)
    if cate is None:
        cate = Category(name='默认分类')
        db.session.add(cate)
    db.session.commit()
    sets.update_site_settings()


@main.before_app_request
def before_app_request():
    if not current_app.config['SITE_INITIATED'] \
            and request.endpoint != 'main.setup' \
            and request.endpoint != 'static':
        return redirect(url_for('main.setup'))


@main.route('/setup', methods=['GET', 'POST'])
def setup():
    if current_app.config['SITE_INITIATED']:
        return redirect('main.index')
    admin = User.query.filter_by(email=current_app.config['SITE_ADMIN_EMAIL']).first()
    if admin is None:
        form = SetupForm01()
        admin = User()
        if form.validate_on_submit():
            admin.email = form.email.data
            admin.name = form.name.data
            admin.password = form.password.data
            admin.is_administrator = True
            db.session.add(admin)
            db.session.commit()
            login_user(admin)
            return redirect(url_for('main.setup'))
    else:
        sets = Settings.query.first()
        form = SetupForm02()
        if form.validate_on_submit():
            sets.site_title = form.title.data
            sets.site_description = form.description.data
            sets.enable_post_comment = form.enable_comment.data
            sets.posts_per_page = form.posts_per_page.data
            sets.comments_per_page = form.comments_per_page.data
            sets.site_initiated = True
            db.session.add(sets)
            db.session.commit()
            sets.update_site_settings()
            login_user(admin)
            return redirect(url_for('main.index'))
    title = '新的开始'
    return render_template("main/gate.html",
                           form=form,
                           title=title)


@main.route('/login', methods=['GET', 'POST'])
def login():
    if not current_user.is_authenticated:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user is None:
                flash('用户名或密码不正确')
                return redirect(url_for('main.login'))
            if user.verify_password(form.password.data):
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
        title = '登陆'
        return render_template('main/gate.html', form=form, title=title)
    else:
        return redirect(url_for('main.index'))


@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@main.route('/index')
@main.route('/')
def index():
    title = 'ImHuWQ'
    query = Post.query.filter_by(_type="article").order_by(Post._edit_date.desc())
    if query.count() <= current_app.config['POSTS_PER_PAGE']:
        posts = query.all()
        pagination = None
    else:
        page = request.args.get('page', 1, type=int)
        pagination = query.paginate(
            page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
        )
        posts = pagination.items
    cates = Category.query.filter_by(_level=0).filter(Category._posts_count != 0).order_by(Category._order).all()
    tags = Tag.query.filter(Tag._posts_count != 0).order_by(Tag._posts_count.desc()).all()
    return render_template('blog/index.html',
                           title=title,
                           posts=posts,
                           cates=cates,
                           tags=tags,
                           detailed=False,
                           pagination=pagination)


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('main/403.html'), 403


@main.app_errorhandler(404)
def not_found(e):
    return render_template('main/404.html'), 404


@main.app_errorhandler(500)
def internal_error(e):
    return render_template('main/500.html'), 500
