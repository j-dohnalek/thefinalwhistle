from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, EqualTo


class RegistrationForm(FlaskForm):
    email = StringField('e-mail', validators=[
        InputRequired()
    ])
    username = StringField('username', validators=[
        InputRequired()
    ])
    password = PasswordField('password', validators=[
        InputRequired(),
        EqualTo('password_confirm', message='Passwords must match')
    ])
    password_confirm = PasswordField('repeat password', validators=[
        InputRequired()
    ])
    accept_tos = BooleanField('I agree to the terms of service', validators=[
        InputRequired()
    ])
    submit = SubmitField('submit')
