from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    # TODO: allow users to login with either username or email
    email = StringField('e-mail/username', validators=[
        InputRequired(message='required')
    ])
    password = PasswordField('password', validators=[
        InputRequired(message='required')
    ])
    remember_me = BooleanField('remember me')
    submit = SubmitField('submit')
