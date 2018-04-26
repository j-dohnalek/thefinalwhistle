from flask_wtf import FlaskForm
from wtforms import StringField, SelectField

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


class EditAccountInfo(FlaskForm):
    real_name = StringField('Real name')
    favourite_team = SelectField('Favourite team', choices=generate_choices_list())

