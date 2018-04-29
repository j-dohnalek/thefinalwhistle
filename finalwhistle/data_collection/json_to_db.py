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

ROOT = os.path.dirname(os.path.realpath(__file__)) + '/'

REFEREE = ROOT + 'football_data/json/list_of_referees.json'
STADIUM = ROOT + 'football_data/json/list_of_stadiums.json'
CLUB_STAFF = ROOT + 'football_data/json/list_of_managers.json'
NEW_FIXTURES = ROOT + 'football_data/json/new_fixtures/*.json'
TRANSFERS = ROOT + 'football_data/json/transfers/*.json'
PLAYERS = ROOT + 'football_data/json/players/*.json'
STATISTICS = ROOT + 'football_data/tmp/E0.csv'
STATISTICS_URL = 'http://www.football-data.co.uk/mmz4281/1718/E0.csv'
STATISTICS_BACKUP = ROOT + 'football_data/csv/E0.csv'
SQL_LITE = ROOT + 'test.db'
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

                    match = None
                    try:
                        match = get_or_create(session, Match,
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

                    # Parse match goals
                    for event in (fixture['details']['goals']):

                        player = session.query(Player).filter_by(name=event['scorer']).first()
                        own_goal = False
                        if 'true' in event['own_goal']:
                            own_goal = True

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

                        penalty = False
                        if assist is None:
                            if own_goal:
                                penalty = False

                        get_or_create(session, Goal,
                                      match=match.match_id,
                                      penalty=penalty,
                                      own_goal=own_goal,
                                      player=player.player_id,
                                      assist_player=assist,
                                      extra_time=extra_time,
                                      minute=event['minute'])

                    # Parse match cards
                    for event in (fixture['details']['cards']):

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
                    for event in (fixture['details']['substitutions']):

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

    print('Parse new fixtures .. OK!')


def parse_statistics():
    """
    Insert all statistics to database


    Div = League Division
    Date = Match Date (dd/mm/yy)
    HomeTeam = Home Team
    AwayTeam = Away Team
    FTHG and HG = Full Time Home Team Goals
    FTAG and AG = Full Time Away Team Goals
    FTR and Res = Full Time Result (H=Home Win, D=Draw, A=Away Win)
    HTHG = Half Time Home Team Goals
    HTAG = Half Time Away Team Goals
    HTR = Half Time Result (H=Home Win, D=Draw, A=Away Win)Match Statistics (where available)
    Attendance = Crowd Attendance
    Referee = Match Referee
    HS = Home Team Shots
    AS = Away Team Shots
    HST = Home Team Shots on Target
    AST = Away Team Shots on Target
    HC = Home Team Corners
    AC = Away Team Corners
    HF = Home Team Fouls Committed
    AF = Away Team Fouls Committed
    HY = Home Team Yellow Cards
    AY = Away Team Yellow Cards
    HR = Home Team Red Cards
    AR = Away Team Red Cards

    For more details see: http://www.football-data.co.uk/notes.txt
    """
    csv_file = STATISTICS_BACKUP

    try:
        try:
            urllib.request.urlretrieve(STATISTICS_URL, STATISTICS)
            csv_file = open(STATISTICS, 'r')
            copyfile(STATISTICS, STATISTICS_BACKUP)
        except urllib.error.URLError:
            pass

        fieldnames = ("Div", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR", "Referee",
                      "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR")

        reader = csv.DictReader(csv_file, fieldnames)
        ignore_first_line = True
        for row in reader:
            if ignore_first_line:
                ignore_first_line = False

            else:
                # Translate the football team to name_short in database
                row["HomeTeam"] = row["HomeTeam"].replace('United', 'Utd')
                row["AwayTeam"] = row["AwayTeam"].replace('United', 'Utd')
                row["HomeTeam"] = row["HomeTeam"].replace('Tottenham', 'Spurs')
                row["AwayTeam"] = row["AwayTeam"].replace('Tottenham', 'Spurs')

                home_team = session.query(Team).filter_by(name_short=row["HomeTeam"]).first()
                away_team = session.query(Team).filter_by(name_short=row["AwayTeam"]).first()

                try:
                    home_team_id = home_team.team_id
                except AttributeError:
                    return '[H] {} vs {} on {}'.format(row["HomeTeam"], row["AwayTeam"], row['Date'])

                try:
                    away_team_id = away_team.team_id
                except AttributeError:
                    return '[A] {} vs {} on {}'.format(row["HomeTeam"], row["AwayTeam"], row['Date'])

                match_day = datetime.strptime(row['Date'], '%d/%m/%y')

                kickoff_casted = sqlalchemy.cast(Match.kickoff, sqlalchemy.Date)
                match_day_casted = sqlalchemy.cast(match_day, sqlalchemy.Date)
                match = session.query(Match).filter(Match.home_team == home_team_id) \
                    .filter(Match.away_team == away_team_id) \
                    .filter(kickoff_casted == match_day_casted).first()
                try:
                    match_id = match.match_id
                except AttributeError:
                    return '[M] {} vs {} on {}'.format(row["HomeTeam"], row["AwayTeam"], row['Date'])

                result = {'H': 1, 'A': 2, 'D': 3}

                get_or_create(session,
                              MatchStatistics,
                              match=match_id,
                              home_team=home_team_id,
                              away_team=away_team_id,
                              home_ft_goals=row['FTHG'],
                              away_ft_goals=row['FTAG'],
                              home_ht_goals=row['HTHG'],
                              away_ht_goals=row['HTAG'],
                              ft_result=result[row['FTR']],
                              ht_result=result[row['HTR']],
                              home_shots=row['HS'],
                              away_shots=row['AS'],
                              home_shots_on_target=row['HST'],
                              away_shots_on_target=row['AST'],
                              home_corners=row['HC'],
                              away_corners=row['AC'],
                              home_fouls=row['HF'],
                              away_fouls=row['AF'],
                              home_yellow_cards=row['HY'],
                              away_yellow_cards=row['AY'],
                              home_red_cards=row['HR'],
                              away_red_cards=row['AR'])

        os.remove(STATISTICS)
    finally:
        session.close()
    print('Parse statistics .. OK!')


if __name__ == '__main__':

    parse_referee()
    parse_league()
    parse_season()
    parse_stadiums()
    parse_teams()
    parse_club_staff()
    parse_players()
    parse_transfers()
    parse_new_fixtures()
    parse_statistics()
    print('Database up to date!')
