from flask import redirect, url_for, render_template, flash
from ...helpers import admin_required
from ...forms import ProfileForm, SiteSettingForm, PasswordSetForm
from ...models import Post, Tag, Category, Settings, User
from . import admin


@admin.route('/index')
@admin.route('/')
@admin_required
def index():
    posts_count = Post.query.filter_by(_type='article').count()
    tags_count = Tag.query.count()
    cates_count = Category.query.count()
    sets = Settings.query.get(1)
    user = User.query.get(1)
    return render_template('admin/index.html', title='后台',
                           posts_count=posts_count, tags_count=tags_count,
                           cates_count=cates_count, sets=sets, user=user)


@admin.route('/site', methods=['GET', 'POST'])
@admin_required
def site():
    form = SiteSettingForm()
    sets = Settings.query.get(1)
    if form.validate_on_submit():
        sets.site_title = form.title.data
        sets.site_description = form.descp.data
        sets.google_analytics_code = form.ga_id.data
        sets.disqus_identifier = form.dq_id.data
        return redirect(url_for('admin.site'))
    form.title.data = sets.site_title
    form.descp.data = sets.site_description
    form.dq_id.data = sets.disqus_identifier
    form.ga_id.data = sets.google_analytics_code
    return render_template('admin/site.html',
                           form=form,
                           sets=sets,
                           title='站点设置')


# below is about user account
@admin.route('/profile', methods=['POST', 'GET'])
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
