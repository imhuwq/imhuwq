# -*- coding: utf8 -*-
"""
    app.forms
    ~~~~~~~~~~

    整个app的Form设计都在这里.
"""

from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField, SelectField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Regexp, NumberRange, ValidationError
from flask import current_app
from .models import Category, Post, User


class SetupForm01(Form):
    email = StringField('登陆邮箱', validators=[DataRequired(), Email()])
    name = StringField('你的名称', validators=[DataRequired(), Length(3, 12, message="名称长度必须在3-12之间"),
                                           Regexp('^[\u2E80-\u9FFFa-zA-Z][\u2E80-\u9FFF0-9a-zA-Z]*$', 0,
                                                  '用户名包括汉字、 字母、数字和下划线, '
                                                  '不能以数字开头')])
    password = PasswordField('登陆密码', validators=[DataRequired(),
                                                 Length(6, 18, message='密码长度必须在6-18之间')])
    submit = SubmitField('下一步')

    def validate_email(self, field):
        if field.data != current_app.config['SITE_ADMIN_EMAIL']:
            raise ValidationError("邮箱必须与您写在'config.py'中的'SITE_ADMIN_EMAIL'相同！")


class SetupForm02(Form):
    title = StringField('网站名称', validators=[DataRequired(), Length(2, 64, message="网站标题长度应该在2-64之间")])
    description = StringField('网站简介', validators=[DataRequired(), Length(1, 128, message="网站简介过长，最多128个字符")])
    enable_comment = SelectField("允许他人评论", choices=[(1, "允许"), (0, "禁止")], coerce=int)
    posts_per_page = IntegerField("每页文章数", default=20, validators=[DataRequired(),
                                                                   NumberRange(1, 50, message="每页最多显示50篇文章")])
    comments_per_page = IntegerField("每页评论数", default=20, validators=[DataRequired(),
                                                                      NumberRange(1, 50, message="每页最多显示50条评论")])

    submit = SubmitField('一切就绪')


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email(message="请输入正确的邮箱地址")])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登陆')

    def validate_password(self, field):
        u = User.query.filter_by(email=self.email.data).first()
        if u is None:
            raise ValidationError('用户名或密码不正确')
        if not u.verify_password(field.data):
            raise ValidationError('用户名或密码不正确')


class PostForm(Form):
    title = StringField('标题', validators=[DataRequired(), Length(1, 64, message='标题过长')])
    content = TextAreaField('正文', validators=[DataRequired()])
    tags = StringField('标签')
    publicity = SelectField("对外公开", choices=[(1, "所有人可见"), (0, "仅自己可见")], coerce=int)
    commendable = SelectField("允许评论", choices=[(1, "允许评论"), (0, "禁止评论")], coerce=int)
    publish = SubmitField('发布')
    post_id = IntegerField('id')
    save = SubmitField('保存')

    def validate_title(self, field):
        post = Post.query.filter_by(_title=field.data).first()
        if post and post.id != self.post_id.data and post.type == 'article':
            raise ValidationError('文章标题重复')


class SiteSettingForm(Form):
    title = StringField('网站标题', validators=[DataRequired()])
    descp = TextAreaField('网站描述', validators=[DataRequired(), Length(4, 30, message='网站描述长度在4-30个字符')])
    dq_id = StringField('Disqus Identifier')
    ga_id = StringField('Google Analytics Track ID')
    submit = SubmitField('修改')


class ProfileForm(Form):
    email = StringField('登陆邮箱', validators=[DataRequired(), Email()])
    name = StringField('你的名称', validators=[DataRequired(), Length(3, 12, message="名称长度必须在3-12之间"),
                                           Regexp('^[\u2E80-\u9FFFa-zA-Z][\u2E80-\u9FFF0-9a-zA-Z]*$', 0,
                                                  '用户名包括汉字、 字母、数字和下划线, '
                                                  '不能以数字开头')])
    submit = SubmitField('提交')


class PasswordSetForm(Form):
    old = PasswordField('旧密码', validators=[DataRequired()])
    new = PasswordField('新密码', validators=[DataRequired(),
                                           Length(6, 18, message='密码长度必须在6-18之间')])
    submit = SubmitField('提交')


class CategoryForm(Form):
    name = StringField('分类名称', validators=[DataRequired(), Length(2, 12, message='分类名称长度在2-12之间')])
    order = IntegerField('排序',  default=0)
    cate_id = IntegerField('id')
    submit = SubmitField('提交')

    def validate_name(self, field):
        name = field.data
        if '/' in name:
            raise ValidationError('分类名中不能包含“/”')
        else:
            cate = Category.query.filter_by(_name=name).first()
            if cate and cate.id != self.cate_id.data:
                raise ValidationError('分类已经存在')
