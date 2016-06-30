from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, ValidationError
from ..models import Category, Post


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


class CategoryForm(Form):
    name = StringField('分类名称', validators=[DataRequired(), Length(2, 12, message='分类名称长度在2-12之间')])
    order = IntegerField('排序', default=0)
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
