from finalwhistle.models.football import Referee, Season, Team
from finalwhistle.models.football import Player, MatchStatistics
from finalwhistle.models.football import Match, Card, Goal, Substitution
from finalwhistle.data_collection.misc import get_or_create, record_exists
import finalwhistle.models.user
import finalwhistle.models.comment
import finalwhistle.models.user
import finalwhistle.models.article

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

NEW_FIXTURES = ROOT + 'cache/json/new_fixtures/*.json'
STATISTICS = ROOT + 'cache/tmp/E0.csv'
STATISTICS_URL = 'http://www.football-data.co.uk/mmz4281/1718/E0.csv'
STATISTICS_BACKUP = ROOT + 'cache/csv/E0.csv'

session = db.session

################################


def parse_new_fixtures():
    """

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

                    season = session.query(Season).filter(sqlalchemy.extract('year', Season.end_year) == end_year).first()
                    home_team = session.query(Team).filter_by(name_short=fixture['home_team']).first()
                    away_team = session.query(Team).filter_by(name_short=fixture['away_team']).first()
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
                        print('{} {} {}'.format(fixture['details']['referee'],
                                                fixture['home_team'],
                                                fixture['away_team']))

                    parse_goals(match.match_id, fixture, fixture['details']['goals'])
                    parse_cards(match.match_id, fixture, fixture['details']['cards'])
                    parse_substitution(match.match_id, fixture, fixture['details']['substitutions'])

    finally:
        session.close()

    print('Parse new fixtures .. OK!')


def parse_goals(match_id, fixture, events):
    """

    :param match_id:
    :param fixture:
    :param events:
    :return:
    """

    for event in events:

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
            # TODO: Write to log
            print('{} {} {}'.format(event['assist'],
                                    fixture['home_team'],
                                    fixture['away_team']))

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
                      match=match_id,
                      penalty=penalty,
                      own_goal=own_goal,
                      player=player.player_id,
                      assist_player=assist,
                      extra_time=extra_time,
                      minute=event['minute'])


def parse_cards(match_id, fixture, events):
    """

    :param match_id:
    :param fixture:
    :param events:
    :return:
    """

    for event in events:

        try:
            player = session.query(Player).filter_by(name=event['player']).first()
            player_id = player.player_id
        except AttributeError:
            # TODO: Write to log
            print('{} {} {}'.format(event['assist'],
                                    fixture['home_team'],
                                    fixture['away_team']))
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
                      match=match_id,
                      yellow=yellow,
                      player=player_id,
                      extra_time=extra_time,
                      minute=event['minute'])


def parse_substitution(match_id, fixture, events):
    """

    :param match_id:
    :param fixture:
    :param events:
    :return:
    """

    for event in events:

        # Player substituted out of the game
        player_out = None
        try:
            player = session.query(Player).filter_by(name=event['out']).first()
            player_out = player.player_id
        except AttributeError:
            # TODO: Write to log
            print('{} {} {}'.format(event['assist'],
                                    fixture['home_team'],
                                    fixture['away_team']))

        # Player substituted into of the game
        player_in = None
        try:
            player = session.query(Player).filter_by(name=event['in']).first()
            player_in = player.player_id
        except KeyError:
            pass

        except AttributeError:
            # TODO: Write to log
            print('{} {} {}'.format(event['assist'],
                                    fixture['home_team'],
                                    fixture['away_team']))

        # Determine if the extra time information is available
        extra_time = 0
        try:
            extra_time = event['additional']
            if extra_time is None:
                extra_time = 0
        except KeyError:
            pass

        get_or_create(session, Substitution,
                      match=match_id,
                      player_out=player_out,
                      player_in=player_in,
                      extra_time=extra_time,
                      minute=event['minute'])


def parse_statistics():
    """
    Download csv file from http://www.football-data.co.uk/englandm.php

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

        columns = ("Div", "Date", "HomeTeam",
                   "AwayTeam", "FTHG", "FTAG",
                   "FTR", "HTHG", "HTAG",
                   "HTR", "Referee", "HS",
                   "AS", "HST", "AST",
                   "HF", "AF", "HC",
                   "AC", "HY", "AY",
                   "HR", "AR")

        reader = csv.DictReader(csv_file, columns)
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

                # H home team win; A away team win; D draw
                result = {'H': 1, 'A': 2, 'D': 3}

                get_or_create(session, MatchStatistics,
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