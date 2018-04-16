from models.football import *
from api import apilib
from sqlalchemy import func

from sqlalchemy import or_
import json


# CONSTANTS #####################################################################


TABLE_JSON = 'cache/tmp/table.json'
EPL = 445  # English Premier League 2017-2018


# CLASS #########################################################################


class Struct:
    """
    Convert the dict to object
    https://stackoverflow.com/questions/1305532
    """
    def __init__(self, **entries):
        self.__dict__.update(entries)


# CONSTANTS #####################################################################


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


def list_all_team_matches(team):
    """
    :param team: sqlalchemy Team object
    :return:
    """

    list_of_matches = []

    matches = Match.query.filter(or_(Match.home_team == team.team_id, Match.away_team == team.team_id)) \
        .join(MatchStatistics, Match.match_id == MatchStatistics.match) \
        .add_columns(Match.home_team,
                     Match.away_team,
                     Match.kickoff,
                     MatchStatistics.home_ft_goals,
                     MatchStatistics.away_ft_goals).all()

    for match in matches:
        match_details = {}

        if match.home_team == team.team_id:
            match_details['home_team'] = team.name
        else:
            home_team = Team.query.filter_by(team_id=match.home_team).first()
            match_details['home_team'] = home_team.name

        if match.away_team == team.team_id:
            match_details['away_team'] = team.name
        else:
            away_team = Team.query.filter_by(team_id=match.away_team).first()
            match_details['away_team'] = away_team.name

        match_details['home_goals'] = match.home_ft_goals
        match_details['away_goals'] = match.away_ft_goals

        match_details['kickoff_time'] = match.kickoff.strftime("%H:%M")
        match_details['kickoff_date'] = match.kickoff.strftime("%d %B %Y")

        list_of_matches.append(match_details)

    return list_of_matches


def list_team_players(team, exclude_transferred=True):

    player_list = []

    if exclude_transferred:
        players = Player.query.filter(Player.transferred_out == 0).filter(Player.current_team == team.team_id).all()
    else:
        players = Player.query.filter(Player.current_team == team.team_id).all()

    for player in players:

        player_information = {
            'id': player.player_id,
            'name': player.name,
            'shirt_number': player.shirt_number,
            'position': player.position
        }

        player_list.append(player_information)

    return player_list


def get_team_information(id):

    team_information = {}

    team = Team.query\
        .join(Stadium, Team.stadium == Stadium.stadium_id)\
        .add_columns(Team.team_id, Team.name, Team.api_id, Stadium.name.label('stadium'))\
        .filter(Team.team_id == id).first()

    if team is not None:

        club_staff = []
        for staff in ClubStaff.query.filter_by(team=team.team_id).all():
            club_staff.append(staff.name)

        source = '/v1/teams/{}'.format(team.api_id)

        # renew every 2000 minutes
        team_json = apilib.fetch_api_data(source, 2000)
        team_information['name'] = team.name
        team_information['crestUrl'] = team_json['crestUrl']
        team_information['stadium'] = team.stadium
        team_information['club_staff'] = club_staff
        team_information['matches'] = list_all_team_matches(team)
        team_information['players'] = list_team_players(team)

        return team_information
    else:
        # Go to 404
        return ''


def get_all_players():

    players = []
    for team in get_all_teams():

        # Convert dict to object
        team_obj = Struct(**team)

        for player in list_team_players(team_obj, exclude_transferred=False):
            players.append(player)

    return players


def get_player_information(id):

    player_information = {}
    player = Player.query.filter_by(player_id=id).first()

    if player is not None:

        player_information['name'] =  player.name
        player_information['position'] = player.position
        player_information['shirt_number'] = player.shirt_number
        try:
            player_information['dob'] = player.dob.strftime("%d %B %Y")
        except AttributeError:
            player_information['dob'] = ""

        player_information['weight'] = player.weight
        player_information['height'] = player.height

        # TODO: team player plays in
        team = Team.query.filter_by(team_id=player.current_team).first()
        player_information['team'] = team.name
        # TODO: count all goals
        player_information['goals_scored'] = Goal.query.filter_by(player=player.player_id).count()
        player_information['goals_assisted'] = Goal.query.filter_by(assist_player=player.player_id).count()
        # TODO: count all cards
        player_information['yellow_cards'] = Card.query.filter_by(player=player.player_id).filter(Card.yellow == True).count()
        player_information['red_cards'] = Card.query.filter_by(player=player.player_id).filter(Card.yellow == False).count()

        return player_information

    else:
        # Go to 404
        return ''
