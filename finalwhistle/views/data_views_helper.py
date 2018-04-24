import finalwhistle.apis.fd_api as fd_api
from finalwhistle.models.football import *
from sqlalchemy import or_, desc, func, asc
import json
from flask import request

# CONSTANTS #####################################################################


ROOT = 'finalwhistle/'

CLUB_CRESTS = ROOT + 'cache/club_crests.json'
TABLE_JSON = ROOT + 'cache/tmp/table.json'
PLAYER_IMAGES = ROOT + 'cache/players_images.json'

EPL = 445  # English Premier League 2017-2018
STATS = ['Shots', 'Shots on Target', 'Corners', 'Fouls', 'Yellow Cards', 'Red Cards']

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
    """
    Parse the latest league table from the JSON file
    :return: league table dict
    """
    with open(TABLE_JSON) as json_file:
        table = json.load(json_file)

    league_table = {}
    for key, value in table.items():

        print(value['club'])
        team = Team.query.filter(Team.name == value['club']).first()

        if team is None:
            team = Team.query.filter(Team.name_short == value['club']).first()

        team_row = {
            "club_id": team.team_id,
            "club_short": team.name_short,
            "club": value['club'],
            "played": value['played'],
            "won": value['won'],
            "drawn": value['drawn'],
            "lost": value['lost'],
            "gf": value['gf'],
            "ga": value['ga'],
            "gd": value['gd'],
            "points": value['points']
        }

        league_table[key] = team_row

    return league_table


def get_all_teams():
    """
    Fetch all teams in the Premier League
    :return: dict
    """

    source = '/v1/competitions/{}/teams'.format(EPL)
    
    # renew every 60 minutes
    teams = fd_api.fetch_api_data(source, 60)
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
    List all team matches
    :param team: SQLAlchemy Team object
    :return: dict
    """

    list_of_matches = []

    matches = Match.query.filter(or_(Match.home_team == team.team_id, Match.away_team == team.team_id)) \
        .join(MatchStatistics, Match.match_id == MatchStatistics.match) \
        .add_columns(Match.home_team,
                     Match.away_team,
                     Match.kickoff,
                     MatchStatistics.home_ft_goals,
                     MatchStatistics.away_ft_goals).order_by(desc(Match.kickoff)).all()

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
    """
    List all players assigned to the team
    :param team: team SQLAlchemy object
    :param exclude_transferred: do not list players transferred out
    :return: dict
    """

    player_list = []

    if exclude_transferred:
        players = Player.query.filter(Player.transferred_out == 0)\
            .filter(Player.current_team == team.team_id).all()
    else:
        players = Player.query.filter(Player.current_team == team.team_id).all()

    for player in players:

        player_information = {
            'id': player.player_id,
            'name': player.name,
            'shirt_number': "",
            'position': "",
            'img': get_player_image(player.name, small=True)
        }

        if player.shirt_number is not None:
            player_information['shirt_number'] = player.shirt_number

        if player.shirt_number is not None:
            player_information['position'] = player.position

        player_list.append(player_information)

    return player_list


def get_team_information(id):
    """
    Get information per team
    :param id: team database id
    :return: dict
    """

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
        team_json = fd_api.fetch_api_data(source, 2000)
        team_information['name'] = team.name
        team_information['crestUrl'] = team_json['crestUrl']
        team_information['stadium'] = team.stadium
        team_information['club_staff'] = club_staff
        team_information['matches'] = list_all_team_matches(team)
        team_information['players'] = list_team_players(team)

        return team_information
    else:
        return None


def get_all_players():
    """
    List all players in database
    :return: dict
    """
    players = []
    for team in get_all_teams():
        # Convert dict to object
        team_obj = Struct(**team)
        for player in list_team_players(team_obj, exclude_transferred=False):
            players.append(player)
    return players


def get_player_image(name, small=True):
    """
    Match name of player to image
    Images are sourced via premierleague.com website
    :param name: players full name
    :param small: boolean true for 40x40px false 250x250px
    :return: url link to the players picture
    """
    small_link = 'https://platform-static-files.s3.amazonaws.com/premierleague/photos/players/40x40/{}.png'
    large_link = 'https://platform-static-files.s3.amazonaws.com/premierleague/photos/players/250x250/{}.png'

    with open(PLAYER_IMAGES) as openfile:
        image = json.load(openfile)

    try:
        player_id = image[name]
    except KeyError:
        player_id = 'Photo-Missing'

    if small:
        return small_link.format(player_id)
    return large_link.format(player_id)


def get_player_information(id):
    """
    Get information for player id
    :param id: players id
    :return: dict
    """

    # Lambda function
    # If string is None return empty string
    # else string supplied
    f = lambda x: '' if x is None else x

    player_information = {}
    player = Player.query.filter_by(player_id=id).first()

    if player is not None:

        player_information['name'] = player.name
        player_information['img'] = get_player_image(player.name, small=False)

        player_information['position'] = f(player.position)
        player_information['shirt_number'] = f(player.shirt_number)
        try:
            player_information['dob'] = player.dob.strftime("%d %B %Y")
        except AttributeError:
            player_information['dob'] = ""

        player_information['weight'] = f(player.weight)
        player_information['height'] = f(player.height)

        team = Team.query.filter_by(team_id=player.current_team).first()

        if player.transferred_out == 1:
            transfer = Transfer.query.filter_by(player=player.player_id).first()
            player_information['team'] = transfer.transfer_to
        else:
            player_information['team'] = team.name

        player_information['goals_scored'] = Goal.query.filter_by(player=player.player_id).count()
        player_information['goals_assisted'] = Goal.query.filter_by(assist_player=player.player_id).count()
        player_information['yellow_cards'] = Card.query.filter_by(player=player.player_id).filter(Card.yellow).count()
        player_information['red_cards'] = Card.query.filter_by(player=player.player_id).filter(not Card.yellow).count()

        return player_information

    else:
        # Go to 404
        return None


def list_all_matches():
    """
    List all matches of the current season
    :return: dict
    """

    with open(CLUB_CRESTS) as jsonfile:
        club_crest = json.load(jsonfile)

    list_of_matches = []

    matches = Match.query.join(MatchStatistics, Match.match_id == MatchStatistics.match) \
        .add_columns(Match.match_id,
                     Match.home_team,
                     Match.away_team,
                     Match.kickoff,
                     MatchStatistics.home_ft_goals,
                     MatchStatistics.away_ft_goals)\
        .order_by(func.DATE(Match.kickoff).desc(), func.TIME(Match.kickoff).asc()).all()

    for match in matches:

        match_details = {'match_id': match.match_id}

        home_team = Team.query.filter_by(team_id=match.home_team).first()
        match_details['home_team'] = home_team.name
        match_details['home_crest'] = club_crest[str(home_team.team_id)]

        away_team = Team.query.filter_by(team_id=match.away_team).first()
        match_details['away_team'] = away_team.name
        match_details['away_crest'] = club_crest[str(away_team.team_id)]

        match_details['home_goals'] = match.home_ft_goals
        match_details['away_goals'] = match.away_ft_goals

        match_details['kickoff_time'] = match.kickoff.strftime("%H:%M")
        match_details['kickoff_date'] = match.kickoff.strftime("%d %B %Y")

        list_of_matches.append(match_details)

    return list_of_matches


def get_match_information(id):
    """
    Get information about a match id
    :param id: match id
    :return: dict
    """

    # Lambda function
    # If string is None return empty string
    # else string supplied
    f = lambda x: '' if x is None else x

    with open(CLUB_CRESTS) as jsonfile:
        club_crest = json.load(jsonfile)

    match = Match.query.join(MatchStatistics, Match.match_id == MatchStatistics.match)\
        .filter(Match.match_id == id) \
        .add_columns(Match.match_id,
                     Match.home_team,
                     Match.away_team,
                     Match.kickoff,
                     MatchStatistics.home_ft_goals,
                     MatchStatistics.home_ht_goals,
                     MatchStatistics.home_shots,
                     MatchStatistics.home_shots_on_target,
                     MatchStatistics.home_corners,
                     MatchStatistics.home_fouls,
                     MatchStatistics.home_yellow_cards,
                     MatchStatistics.home_red_cards,
                     MatchStatistics.away_ft_goals,
                     MatchStatistics.away_ht_goals,
                     MatchStatistics.away_shots,
                     MatchStatistics.away_shots_on_target,
                     MatchStatistics.away_corners,
                     MatchStatistics.away_fouls,
                     MatchStatistics.away_yellow_cards,
                     MatchStatistics.away_red_cards)\
        .order_by(func.DATE(Match.kickoff).desc(), func.TIME(Match.kickoff).asc()).first()

    if match is not None:

        match_information = {}

        home_team = Team.query.filter_by(team_id=match.home_team).first()
        match_information['home_team'] = home_team.name
        match_information['home_crest'] = club_crest[str(home_team.team_id)]

        away_team = Team.query.filter_by(team_id=match.away_team).first()
        match_information['away_team'] = away_team.name
        match_information['away_crest'] = club_crest[str(away_team.team_id)]

        match_information['home_goals'] = match.home_ft_goals
        match_information['away_goals'] = match.away_ft_goals

        match_information['kickoff_time'] = match.kickoff.strftime("%H:%M")
        match_information['kickoff_date'] = match.kickoff.strftime("%d %B %Y")

        goals = Goal.query\
            .filter(Goal.match == id)\
            .join(Player, Goal.player == Player.player_id)\
            .add_columns(Goal.minute, Goal.extra_time, Player.name.label('scorer'), Player.current_team)\
            .order_by(asc(Goal.minute)).all()

        # TODO: add link to player in match details
        match_information['home_scoring_players'] = []
        match_information['away_scoring_players'] = []
        for goal in goals:
            goal_info = {'minute': goal.minute, 'extra_time': f(goal.extra_time), 'scorer': goal.scorer}
            if goal.current_team == match.home_team:
                match_information['home_scoring_players'].append(goal_info)
            else:
                match_information['away_scoring_players'].append(goal_info)

        match_information['home_team_stats'] = {
            'Shots': match.home_shots,
            'Shots on Target': match.home_shots_on_target,
            'Corners': match.home_corners,
            'Fouls': match.home_fouls,
            'Yellow Cards': match.home_yellow_cards,
            'Red Cards': match.home_red_cards,
        }

        match_information['away_team_stats'] = {
            'Shots': match.away_shots,
            'Shots on Target': match.away_shots_on_target,
            'Corners': match.away_corners,
            'Fouls': match.away_fouls,
            'Yellow Cards': match.away_yellow_cards,
            'Red Cards': match.away_red_cards,
        }

        return match_information

    else:
        return None


def get_compare_teams():
    """
    Compare two team together based on goals, cards, won games, lost games, etc.
    :return:
    """

    # No POST request
    if len(request.form) == 0:
        return dict(team1=None, team2=None, error=None)

    data = request.form

    try:
        team1 = int(data['team1'])
    except ValueError:
        return dict(team1=None, team2=None, error='2 clubs required, please select 2 clubs')

    try:
        team2 = int(data['team2'])
    except ValueError:
        return dict(team1=None, team2=None, error='2 clubs required, please select 2 clubs')

    # In case data is submitted manually check if teams exist
    selected_team1 = Team.query.filter_by(team_id=team1)
    selected_team2 = Team.query.filter_by(team_id=team2)

    if selected_team1 is None or selected_team2 is None or team1 == team2:
        return dict(team1=None, team2=None, error='Invalid combination of clubs selected, please choose different clubs')


def fetch_team_statistics(id):
    """
    Fetch statistics for team
    :param id: team database id
    :return: dict
    """

    # Statistic we need: