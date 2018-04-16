from models.football import *
from api import apilib

import json


TABLE_JSON = 'cache/tmp/table.json'
EPL = 445  # English Premier League 2017-2018


def get_league_table():
    # TODO: check if the file is older than x minutes
    # if so attempt to start a thread parallel that will update
    # the json file, also create a lock that only one get request
    # can start a thread
    with open(TABLE_JSON) as json_file:
        return json.load(json_file)


def get_all_teams():
    source = '/v1/competitions/{}/teams'.format(EPL)
    # renew every 60 minutes
    teams = apilib.fetch_api_data(source, 60)
    team_list = []

    for team in teams['teams']:

        club = Team.query.filter_by(api_id=team['id']).first()

        team_list.append(
            {
                'team_id': club.team_id,
                'api_id': team['id'],
                'name': team['name'],
                'crestUrl': team['crestUrl']
            }
        )

    return team_list


def get_team_information(id):

    team_information = {}

    team = Team.query.filter_by(team_id=id).first()

    if team is not None:

        source = '/v1/teams/{}'.format(team.api_id)
        # renew every 2000 minutes
        team_json = apilib.fetch_api_data(source, 2000)
        team_information['name'] = team.name
        team_information['crestUrl'] = team_json['crestUrl']
        # TODO: add stadium
        # TODO: add manager
        # TODO: add matches
        # TODO: add players

    return team_information
