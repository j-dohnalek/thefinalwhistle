from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField, PasswordField
from wtforms.validators import InputRequired, EqualTo, ValidationError, Length

from finalwhistle.views.data_views_helper import get_all_teams
import sqlalchemy

def generate_choices_list():
    """
    Convert dict returned by 'get_all_teams()' into list of tuples
    :return: List of tuples (team_id, team_name) for all teams
    """
    team_list = []

    try:
        for team in get_all_teams():
            try:
                team_list.append((team.get('team_id'), team.get('name')))
            except AttributeError as e:
                print(e)
    except sqlalchemy.exc.OperationalError:
        return []

    return team_list


def user_real_name_or_empty_string():
    try:
        return current_user.real_name
    except AttributeError:
        print('no real name set')
    return ''


def user_fav_team_or_1():
    try:
        id = current_user.supported_team_id
        if not id is (None or ''):
            return id
    except AttributeError:
        print('no fav team selected')
    return 1


class EditAccountInfoForm(FlaskForm):
    real_name = StringField('Real name', default=user_real_name_or_empty_string())
    favourite_team = SelectField('Favourite team', choices=generate_choices_list(), coerce=int, default=user_fav_team_or_1())
    submit = SubmitField('Save changes')


class ChangePasswordForm(FlaskForm):
    current_pw = PasswordField('Current password')
    new_pw = PasswordField('New password', validators=[
        InputRequired(),
        EqualTo('new_pw_repeat', message='Passwords must match')
    ])
    new_pw_repeat = PasswordField('Repeat new password', validators=[
        InputRequired(),
        EqualTo('new_pw', message='Passwords must match')
    ])
    submit = SubmitField('Update password')

    def validate_current_pw(self, current_pw):
        if not current_user.password_valid(current_pw.data):
            raise ValidationError('Incorrect password')

    def validate_new_pw(self, password):
        from finalwhistle.models.user import validate_password
        validate_password(password)
