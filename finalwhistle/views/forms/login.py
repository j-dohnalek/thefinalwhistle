from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired


class LoginForm(FlaskForm):
    # TODO: allow users to login with either username or email
    email = StringField('E-mail address', validators=[
        InputRequired()
    ])
    password = PasswordField('Password', validators=[
        InputRequired()
    ])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Submit')
