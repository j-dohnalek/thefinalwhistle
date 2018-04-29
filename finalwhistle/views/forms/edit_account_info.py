from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField

from finalwhistle.views.data_views_helper import get_all_teams


def generate_choices_list():
    """
    Convert dict returned by 'get_all_teams()' into list of tuples
    :return: List of tuples (team_id, team_name) for all teams
    """
    team_list = []
    for team in get_all_teams():
        try:
            team_list.append((team.get('team_id'), team.get('name')))
        except AttributeError as e:
            print(e)
    return team_list


def user_real_name_or_blank():
    try:
        return current_user.real_name
    except AttributeError:
        print('no real name set')
    return ''

def user_fav_team_or_blank():
    try:
        id = current_user.supported_team_id
        if not id is (None or ''):
            return id
    except AttributeError:
        print('no fav team selected')
        return 1


class EditAccountInfoForm(FlaskForm):
    real_name = StringField('Real name', default=user_real_name_or_blank())
    favourite_team = SelectField('Favourite team', choices=generate_choices_list(), coerce=int, default=user_fav_team_or_blank())
    submit = SubmitField(label='Save changes')

class ChangePassword(FlaskForm):
    current_pw = StringField('Current password')
    new_pw = StringField('New password')
    new_pw_repeat = StringField('Repeat new password')