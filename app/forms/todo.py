from flask_wtf import Form
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class TaskForm(Form):
    text = StringField('创建新任务', validators=[DataRequired(), Length(1, 120, message="内容长度1-120个字符")])
