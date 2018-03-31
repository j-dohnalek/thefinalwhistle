from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length


class LoginForm(FlaskForm):
    email = StringField('e-mail', validators=[
        InputRequired()
    ])
    password = PasswordField('password', validators=[
        InputRequired(),
        Length(min=8, max=30)
    ])
