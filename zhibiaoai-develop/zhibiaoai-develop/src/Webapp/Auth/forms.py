"""
验证表单，定义WTForms表单类
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
from Webapp.models import USER

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64)])
    email = StringField('邮箱', validators=[DataRequired(), Email(), Length(1, 120)])
    password = PasswordField('密码', validators=[DataRequired(), Length(6)])
    password2 = PasswordField('确认密码',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = USER.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已存在')

    def validate_email(self, email):
        user = USER.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('邮箱已被注册')