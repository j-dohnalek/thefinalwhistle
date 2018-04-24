from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, EqualTo, ValidationError

from finalwhistle.models.user import User


class RegistrationForm(FlaskForm):
    email = StringField('E-mail', validators=[
        InputRequired()
    ])
    username = StringField('Username', validators=[
        InputRequired()
    ])
    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('password_confirm', message='Passwords must match')
    ])
    password_confirm = PasswordField('Repeat password', validators=[
        InputRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    accept_tos = BooleanField('I agree to the terms of service', validators=[
        InputRequired()
    ])
    submit = SubmitField('Submit')

    # methods called 'validate_NAME' will act as validators for the form field 'NAME'
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already in use')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Email already in use')