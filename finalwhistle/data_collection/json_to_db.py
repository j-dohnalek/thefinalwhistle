from finalwhistle.models.football import Referee, League, Season, Stadium, Team
from finalwhistle.models.football import ClubStaff, Player, Transfer, MatchStatistics
from finalwhistle.models.football import Match, Card, Goal, Substitution
from finalwhistle.data_collection.misc import get_or_create, record_exists

from finalwhistle import db

from datetime import datetime
from shutil import copyfile
import json
import glob
import sqlalchemy
import os
import csv
import urllib.request
import urllib.error

#################################

ROOT = os.path.dirname(os.path.realpath(__file__)) + '/football_data/'

# list of referees
REFEREE = ROOT + 'json/list_of_referees.json'

# list of stadiums
STADIUM = ROOT + 'json/list_of_stadiums.json'

# list of club staff
CLUB_STAFF = ROOT + 'json/list_of_managers.json'

# list of fixtures
NEW_FIXTURES = ROOT + 'json/new_fixtures/*.json'

# list of all transfers
TRANSFERS = ROOT + 'json/transfers/*.json'

# lists of all players
PLAYERS = ROOT + 'json/players/*.json'


# lists of all players
NEW_PLAYERS = ROOT + 'tmp/new_players.json'

SEASON = 1

session = db.session

################################


def parse_referee():
    """ Insert all referees to database """

    try:

        with open(REFEREE) as outfile:
            referees = json.load(outfile)
            list_of_referees = referees[0]['referees']

        for referee in list_of_referees:
            get_or_create(session, Referee, name=referee)

    finally:
        session.close()

    print('Parse referee .. OK!')


def parse_league():
    """ Insert league to database """

    try:
        get_or_create(session, League, name='Premier League', api_id=445)
    finally:
        session.close()
    print('Parse league .. OK!')


def parse_season():
    """ Insert season to database """

    try:
        s = '2018-01-01'
        date_format = '%Y-%m-%d'
        date = datetime.strptime(s, date_format)
        if not record_exists(session, Season, end_year=date):
            get_or_create(session, Season, end_year=date)
    finally:
        session.close()

    print('Parse season .. OK!')


def parse_stadiums():
    """ Insert all stadiums to database """

    try:

        with open(STADIUM) as outfile:
            stadiums = json.load(outfile)
        for stadium in stadiums:
            get_or_create(session, Stadium, name=stadium['stadium'])
    finally:
        session.close()

    print('Parse stadiums .. OK!')


def parse_teams():
    """ Insert all teams to database """

    try:
        with open(STADIUM) as outfile:
            clubs = json.load(outfile)

        for club in clubs:
            stadium = session.query(Stadium).filter_by(name=club['stadium']).first()
            league = session.query(League).filter_by(name='Premier League').first()
            get_or_create(session,
                          Team,
                          name=club['club'],
                          name_short=club['club_short'],
                          stadium=stadium.stadium_id,
                          league=league.league_id,
                          api_id=club['api_id'])
    finally:
        session.close()

    print('Parse teams .. OK!')


def parse_club_staff():
    """ Insert all club staff to database """

    try:

        with open(CLUB_STAFF) as outfile:
            clubs = json.load(outfile)

        for club in clubs:
            team = session.query(Team).filter(Team.name.like("%" + club['club'] + "%")).first()
            for manager in club['managers']:
                get_or_create(session, ClubStaff, team=team.team_id, name=manager, role='manager')
    finally:
        session.close()

    print('Parse club staff .. OK!')


def parse_players():
    """ Insert all player to database """

    try:

        for src in glob.glob(PLAYERS):

            with open(src) as outfile:
                players = json.load(outfile)

            for club in players:
                team = session.query(Team).filter_by(name=club['club']).first()
                for player in club['players']:

                    date_format = '%d/%m/%Y'
                    date = datetime.strptime(player['dob'], date_format)

                    if not record_exists(session, Player, name=player['name']):
                        get_or_create(session, Player,
                                      name=player['name'],
                                      current_team=team.team_id,
                                      shirt_number=player['shirt_number'],
                                      height=player['height'].replace('cm', ''),
                                      weight=player['weight'].replace('kg', ''),
                                      position=player['position'],
                                      nationality=player['nationality'],
                                      dob=date)

    finally:
        session.close()

    print('Parse players .. OK!')


def parse_transfers():
    """ Insert all transfers to database """

    try:

        for src in glob.glob(TRANSFERS):
            with open(src) as outfile:
                transfers = json.load(outfile)

            for transfer in transfers['transfers']:

                team1 = record_exists(session, Team, name=transfer['team1'])
                team2 = record_exists(session, Team, name=transfer['team2'])

                if team1 or team2:

                    if team1:
                        team = session.query(Team).filter_by(name=transfer['team1']).first()
                    else:
                        team = session.query(Team).filter_by(name=transfer['team2']).first()

                    team_to = transfer['team1']
                    team_from = transfer['team2']

                    if transfer['direction'] == 'out':
                        team_to = transfer['team2']
                        team_from = transfer['team1']

                    player = session.query(Player).filter_by(name=transfer['name']).first()
                    if player is None:
                        player = get_or_create(session, Player,
                                               name=transfer['name'],
                                               transferred_out=True,
                                               current_team=team.team_id)

                    transfer_date = datetime.strptime(transfer['date'], '%d %B %Y')
                    end_year = transfer_date.year

                    # The season is scheduled to finish on May (Jun, Jul contingency)
                    season_end = datetime.strptime('31 Jul {}'.format(transfer_date.year), '%d %b %Y')
                    if transfer_date > season_end:
                        end_year = transfer_date.year + 1
                    season = session.query(Season).filter(
                        sqlalchemy.extract('year', Season.end_year) == end_year).first()

                    get_or_create(session, Transfer,
                                  player=player.player_id,
                                  transfer_window_end=transfer_date,
                                  transfer_from=team_from,
                                  transfer_to=team_to,
                                  details=transfer['details'],
                                  season=season.season_id)
    finally:
        session.close()

    print('Parse transfers .. OK!')


def parse_new_players():
    """ Insert all new player found on premierleague.com  """

    try:
        with open(NEW_PLAYERS) as outfile:
            players = json.load(outfile)

        for player in players:

            new_club = Team.query.filter_by(name=player['new_club']).first()
            old_club = Team.query.filter_by(name=player['old_club']).first()

            consider_inserting = False
            team_id = -1

            if new_club is None and old_club is None:
                # Transfer from team in different league to team in different league
                pass

            if new_club is not None and old_club is None:
                # Transfer from team in different league to PL team
                consider_inserting = True
                team_id = new_club.team_id

            if new_club is None and old_club is not None:
                # Transfer from PL team to team in different league
                pass

            if new_club is not None and old_club is not None:

                # Transfer from PL team to PL team
                consider_inserting = True
                team_id = new_club.team_id

            if consider_inserting:

                date_format = '%d/%m/%Y'
                date = None

                try:
                    date = datetime.strptime(player['dob'], date_format)
                except ValueError:
                    pass

                shirt_number = None
                if player['shirt_number'] != '-1':
                    shirt_number = player['shirt_number']

                if not record_exists(session, Player, name=player['name']):
                    get_or_create(session, Player,
                                  name=player['name'],
                                  current_team=team_id,
                                  shirt_number=shirt_number,
                                  height=player['height'].replace('cm', ''),
                                  weight=player['weight'].replace('kg', ''),
                                  position=player['position'],
                                  nationality=player['nationality'],
                                  dob=date)

    finally:
        session.close()

    print('Parse new players .. OK!')


def parse_new_fixtures():
    """
    Insert all matches to database
    :return:
    """
    try:

        for src in glob.glob(NEW_FIXTURES):

            with open(src) as outfile:
                match_day = json.load(outfile)

            for fixtures in match_day:
                match_date = fixtures['date']
                for fixture in fixtures['fixtures']:

                    kickoff_datetime = "{} {}".format(match_date, fixture['details']['kick_off'])
                    kickoff = datetime.strptime(kickoff_datetime, '%A %d %B %Y %H:%M')

                    # The season is scheduled to finish on May
                    season_end = datetime.strptime('31 Jul {}'.format(kickoff.year), '%d %b %Y')
                    if kickoff > season_end:
                        end_year = kickoff.year + 1
                    else:
                        end_year = kickoff.year

                    season = session.query(Season).filter(
                        sqlalchemy.extract('year', Season.end_year) == end_year).first()

                    home_team = session.query(Team).filter_by(name_short=fixture['home_team']).first()
                    away_team = session.query(Team).filter_by(name_short=fixture['away_team']).first()

                    # Translate special cases
                    fixture['details']['referee'] = fixture['details']['referee'].replace('Anthony', 'Andy')

                    referee = session.query(Referee).filter_by(name=fixture['details']['referee']).first()

                    try:
                        get_or_create(session, Match,
                                      home_team=home_team.team_id,
                                      away_team=away_team.team_id,
                                      kickoff=kickoff,
                                      season=season.season_id,
                                      main_referee=referee.referee_id)

                    except AttributeError:
                        print('[Referee] {} {} {} {}'.format(fixture['details']['referee'],
                                                             fixture['home_team'],
                                                             fixture['away_team'],
                                                             fixtures['date']))

    finally:
        session.close()

    print('Parse new fixtures .. OK!')


def parse_match_statistics():
    """
    Insert all matches to database
    :return:
    """
    try:

        for src in glob.glob(NEW_FIXTURES):

            with open(src) as outfile:
                match_day = json.load(outfile)

            for fixtures in match_day:
                match_date = fixtures['date']
                for fixture in fixtures['fixtures']:

                    kickoff_datetime = "{} {}".format(match_date, fixture['details']['kick_off'])
                    kickoff = datetime.strptime(kickoff_datetime, '%A %d %B %Y %H:%M')

                    # The season is scheduled to finish on May
                    season_end = datetime.strptime('31 Jul {}'.format(kickoff.year), '%d %b %Y')
                    if kickoff > season_end:
                        end_year = kickoff.year + 1
                    else:
                        end_year = kickoff.year

                    season = session.query(Season).filter(
                        sqlalchemy.extract('year', Season.end_year) == end_year).first()

                    home_team = session.query(Team).filter_by(name_short=fixture['home_team']).first()
                    away_team = session.query(Team).filter_by(name_short=fixture['away_team']).first()

                    # Translate special cases
                    fixture['details']['referee'] = fixture['details']['referee'].replace('Anthony', 'Andy')

                    referee = session.query(Referee).filter_by(name=fixture['details']['referee']).first()

                    match = Match.query.filter(Match.home_team == home_team.team_id)\
                        .filter(Match.away_team == away_team.team_id)\
                        .filter(Match.kickoff == kickoff)\
                        .filter(Match.season == season.season_id)\
                        .filter(Match.main_referee == referee.referee_id).first()

                    ft_goals_home = fixture['score'].split('-')[0]
                    ft_goals_away = fixture['score'].split('-')[1]

                    shots_home = 0
                    shots_away = 0
                    try:
                        shots_home = fixture['details']['statistic']['shots']['home']
                        shots_away = fixture['details']['statistic']['shots']['away']
                    except KeyError:
                        pass

                    shots_on_target_home = 0
                    shots_on_target_away = 0
                    try:
                        shots_on_target_home = fixture['details']['statistic']['shots_on_target']['home']
                        shots_on_target_away = fixture['details']['statistic']['shots_on_target']['away']
                    except KeyError:
                        pass

                    fouls_home = 0
                    fouls_away = 0
                    try:
                        fouls_home = fixture['details']['statistic']['fouls_conceded']['home']
                        fouls_away = fixture['details']['statistic']['fouls_conceded']['away']
                    except KeyError:
                        pass

                    corners_home = 0
                    corners_away = 0
                    try:
                        corners_home = fixture['details']['statistic']['corners']['home']
                        corners_away = fixture['details']['statistic']['corners']['away']
                    except KeyError:
                        pass

                    yellow_cards_home = 0
                    yellow_cards_away = 0
                    try:
                        yellow_cards_home = fixture['details']['statistic']['yellow_cards']['home']
                        yellow_cards_away = fixture['details']['statistic']['yellow_cards']['away']
                    except KeyError:
                        pass

                    red_cards_home = 0
                    red_cards_away = 0
                    try:
                        red_cards_home = fixture['details']['statistic']['red_cards']['home']
                        red_cards_away = fixture['details']['statistic']['red_cards']['away']
                    except KeyError:
                        pass

                    get_or_create(session, MatchStatistics,
                                  match=match.match_id,
                                  home_team=home_team.team_id, away_team=away_team.team_id,
                                  home_ft_goals=ft_goals_home, away_ft_goals=ft_goals_away,
                                  home_shots=shots_home, away_shots=shots_away,
                                  home_shots_on_target=shots_on_target_home, away_shots_on_target=shots_on_target_away,
                                  home_corners=corners_home, away_corners=corners_away,
                                  home_fouls=fouls_home, away_fouls=fouls_away,
                                  home_yellow_cards=yellow_cards_home, away_yellow_cards=yellow_cards_away,
                                  home_red_cards=red_cards_home, away_red_cards=red_cards_away)

    finally:
        session.close()

    print('Parse match statistics .. OK!')


def parse_player_statistics():
    """
    Insert all matches to database
    :return:
    """
    try:

        for src in glob.glob(NEW_FIXTURES):

            with open(src) as outfile:
                match_day = json.load(outfile)

            for fixtures in match_day:
                match_date = fixtures['date']
                for fixture in fixtures['fixtures']:

                    kickoff_datetime = "{} {}".format(match_date, fixture['details']['kick_off'])
                    kickoff = datetime.strptime(kickoff_datetime, '%A %d %B %Y %H:%M')

                    # The season is scheduled to finish on May
                    season_end = datetime.strptime('31 Jul {}'.format(kickoff.year), '%d %b %Y')
                    if kickoff > season_end:
                        end_year = kickoff.year + 1
                    else:
                        end_year = kickoff.year

                    season = session.query(Season).filter(
                        sqlalchemy.extract('year', Season.end_year) == end_year).first()

                    home_team = session.query(Team).filter_by(name_short=fixture['home_team']).first()
                    away_team = session.query(Team).filter_by(name_short=fixture['away_team']).first()

                    # Translate special cases
                    fixture['details']['referee'] = fixture['details']['referee'].replace('Anthony', 'Andy')

                    referee = session.query(Referee).filter_by(name=fixture['details']['referee']).first()

                    match = Match.query.filter(Match.home_team == home_team.team_id) \
                        .filter(Match.away_team == away_team.team_id) \
                        .filter(Match.kickoff == kickoff) \
                        .filter(Match.season == season.season_id) \
                        .filter(Match.main_referee == referee.referee_id).first()

                    # Parse match goals
                    for event in fixture['details']['goals']:

                        player = session.query(Player).filter_by(name=event['scorer']).first()

                        own_goal = False
                        if 'true' in event['own_goal']:
                            own_goal = True

                        penalty = False
                        if 'true' in event['penalty']:
                            penalty = True

                        assist = None
                        try:
                            player_assist = session.query(Player).filter_by(name=event['assist']).first()
                            assist = player_assist.player_id
                        except KeyError:
                            pass

                        except AttributeError:
                            print('[Player] {} {} {} {}'.format(event['assist'],
                                                                fixture['home_team'],
                                                                fixture['away_team'],
                                                                fixtures['date']))

                        extra_time = 0
                        try:
                            extra_time = event['additional']
                            if extra_time is None:
                                extra_time = 0
                        except KeyError:
                            pass

                        get_or_create(session, Goal,
                                      match=match.match_id,
                                      penalty=penalty,
                                      own_goal=own_goal,
                                      player=player.player_id,
                                      assist_player=assist,
                                      extra_time=extra_time,
                                      minute=event['minute'])

                    # Parse match cards
                    for event in fixture['details']['cards']:

                        try:
                            player = session.query(Player).filter_by(name=event['player']).first()
                            player_id = player.player_id
                        except AttributeError:
                            print('[Player] {} {} {} {}'.format(event['player'],
                                                                fixture['home_team'],
                                                                fixture['away_team'],
                                                                fixtures['date']))
                            break

                        extra_time = 0
                        try:
                            extra_time = event['additional']
                            if extra_time is None:
                                extra_time = 0

                        except KeyError:
                            pass

                        yellow = True
                        if event['card'] == 'red':
                            yellow = False

                        get_or_create(session, Card,
                                      match=match.match_id,
                                      yellow=yellow,
                                      player=player_id,
                                      extra_time=extra_time,
                                      minute=event['minute'])

                    # Parse match substitutions
                    for event in fixture['details']['substitutions']:

                        player_out = None
                        try:
                            player = session.query(Player).filter_by(name=event['out']).first()
                            player_out = player.player_id
                        except AttributeError:
                            print('[Player] {} {} {} {}'.format(event['out'],
                                                                fixture['home_team'],
                                                                fixture['away_team'],
                                                                fixtures['date']))
                            break

                        player_in = None
                        try:
                            player = session.query(Player).filter_by(name=event['in']).first()
                            player_in = player.player_id
                        except KeyError:
                            pass

                        except AttributeError:
                            print('[Player] {} {} {} {}'.format(event['in'],
                                                                fixture['home_team'],
                                                                fixture['away_team'],
                                                                fixtures['date']))
                            break

                        extra_time = 0
                        try:
                            extra_time = event['additional']
                            if extra_time is None:
                                extra_time = 0

                        except KeyError:
                            pass

                        get_or_create(session, Substitution,
                                      match=match.match_id,
                                      player_out=player_out,
                                      player_in=player_in,
                                      extra_time=extra_time,
                                      minute=event['minute'])

    finally:
        session.close()

    print('Parse player statistics .. OK!')


if __name__ == '__main__':

    parse_referee()
    parse_league()
    parse_season()
    parse_stadiums()
    parse_teams()
    parse_club_staff()
    parse_players()
    parse_transfers()
    parse_new_players()
    parse_new_fixtures()
    parse_match_statistics()
    parse_player_statistics()
    print('Database up to date!')
