from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    email = StringField('e-mail', validators=[])
    password = PasswordField('password', validators=[])
    remember_me = BooleanField('remember me')
    submit = SubmitField('submit')