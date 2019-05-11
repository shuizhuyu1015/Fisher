"""
    create by Gray 2019-04-28
"""
from wtforms import Form, StringField
from wtforms.validators import DataRequired, Length, Email


class BaseForm(Form):
    email = StringField(validators=[DataRequired(), Length(8, 64), Email(message='电子邮箱不符合规范')])
