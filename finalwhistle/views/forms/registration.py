from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, EqualTo, ValidationError

from finalwhistle.models.user import User


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
        InputRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    accept_tos = BooleanField('I agree to the terms of service', validators=[
        InputRequired()
    ])
    submit = SubmitField('submit')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already in use')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already in use')