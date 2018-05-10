from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, EqualTo, ValidationError, Email, DataRequired

from finalwhistle.models.user import User


class RegistrationForm(FlaskForm):
    email = StringField('E-mail', validators=[
        InputRequired(),
        Email()
    ])
    username = StringField('Username', validators=[
        InputRequired()
    ])
    real_name = StringField('Name', validators=[
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
    accept_tos = BooleanField('accept_tos', validators=[
        DataRequired()
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

    def validate_password(self, password):
        from finalwhistle.models.user import validate_password
        try:
            validate_password(password.data)
        except:
            raise ValidationError('Please enter a password with at least 1 uppercase letter, 1 lowercase letter and 1 number')
