from server import app
from server import db
from football import Referee, League, Season, Stadium, Team
from football import ClubStaff, Player, Transfer, MatchStatistics
from football import Match, Card, Goal, Substitution
from misc import get_or_create, record_exists

from flask import render_template
import json
from datetime import datetime
import glob
import sqlalchemy
import os
import csv
import urllib.request

#################################

JSON_PATH = 'cache/json'

REFEREE = JSON_PATH + '/list_of_referees.json'
STADIUM = JSON_PATH + '/list_of_stadiums.json'
CLUB_STAFF = JSON_PATH + '/list_of_managers.json'
OLD_FIXTURES = JSON_PATH + '/fixtures/*.json'
NEW_FIXTURES = JSON_PATH + '/new_fixtures/*.json'
TRANSFERS = JSON_PATH + '/transfers/*.json'

STATISTICS = 'cache/tmp/E0.csv'
STATISTICS_URL = 'http://www.football-data.co.uk/mmz4281/1718/E0.csv'

STATIC_TEMPLATE = 'static/index.html'

################################


@app.route('/', methods=['GET'])
def index():
    return render_template(STATIC_TEMPLATE, message='It Works! Next: Create DB')


@app.route('/delete', methods=['GET'])
def delete_db():
    os.remove('test.db')
    return render_template(STATIC_TEMPLATE, message='Database deleted! Next: Create DB')


@app.route('/create', methods=['GET'])
def create():
    db.create_all(app=app)
    return render_template(STATIC_TEMPLATE, message='Create DB .. OK! Next: Parse referee')


@app.route('/referee', methods=['GET'])
def parse_referee():

    with open(REFEREE) as outfile:
        referees = json.load(outfile)
        list_of_referees = referees[0]['referees']

    for referee in list_of_referees:
        get_or_create(db.session, Referee, name=referee)

    return render_template(STATIC_TEMPLATE, message='Parse referee .. OK! Next: Parse league')


@app.route('/league', methods=['GET'])
def parse_league():
    get_or_create(db.session, League, name='Premier League')
    return render_template(STATIC_TEMPLATE, message='Parse league .. OK! Next: Parse season')


@app.route('/season', methods=['GET'])
def parse_season():
    s = '2018-01-01'
    date_format = '%Y-%m-%d'
    date = datetime.strptime(s, date_format)
    get_or_create(db.session, Season, end_year=date)
    return render_template(STATIC_TEMPLATE, message='Parse season .. OK! Next: Parse stadiums')


@app.route('/stadiums', methods=['GET'])
def parse_stadiums():

    with open(STADIUM) as outfile:
        stadiums = json.load(outfile)
    for stadium in stadiums:
        get_or_create(db.session, Stadium, name=stadium['stadium'])
    return render_template(STATIC_TEMPLATE, message='Parse stadiums .. OK! Next: Parse teams')


@app.route('/teams', methods=['GET'])
def parse_teams():
    with open(STADIUM) as outfile:
        clubs = json.load(outfile)

    for club in clubs:

        stadium = Stadium.query.filter_by(name=club['stadium']).first()
        league = League.query.filter_by(name='Premier League').first()
        get_or_create(db.session, Team, name=club['club'], name_short=club['club_short'],
                      stadium=stadium.stadium_id, league=league.league_id)

    return render_template(STATIC_TEMPLATE, message='Parse teams .. OK! Next: Parse club staff')


@app.route('/clubstaff', methods=['GET'])
def parse_club_staff():

    with open(CLUB_STAFF) as outfile:
        clubs = json.load(outfile)

    for club in clubs:
        team = Team.query.filter(Team.name.like("%" + club['club'] + "%")).first()
        for manager in club['managers']:
            get_or_create(db.session, ClubStaff, team=team.team_id, name=manager, role='manager')

    return render_template(STATIC_TEMPLATE, message='Parse club staff .. OK! Next: Parse players')


@app.route('/players', methods=['GET'])
def parse_players():

    for src in glob.glob("cache/json/players/*.json"):

        with open(src) as outfile:
            players = json.load(outfile)

        for club in players:
            team = Team.query.filter_by(name=club['club']).first()
            for player in club['players']:

                date_format = '%d/%m/%Y'
                date = datetime.strptime(player['dob'], date_format)

                if not record_exists(db.session, Player, name=player['name']):

                    get_or_create(db.session, Player,
                                  name=player['name'],
                                  current_team=team.team_id,
                                  shirt_number=player['shirt_number'],
                                  height=player['height'].replace('cm', ''),
                                  weight=player['weight'].replace('kg', ''),
                                  position=player['position'],
                                  nationality=player['nationality'],
                                  dob=date)

    return render_template(STATIC_TEMPLATE, message='Parse players .. OK! Next: Parse transfers')


@app.route('/transfers', methods=['GET'])
def parse_transfers():

    for src in glob.glob(TRANSFERS):
        with open(src) as outfile:
            transfers = json.load(outfile)

        for transfer in transfers['transfers']:

            team1 = record_exists(db.session, Team, name=transfer['team1'])
            team2 = record_exists(db.session, Team, name=transfer['team2'])

            if team1 or team2:

                if team1:
                    team = Team.query.filter_by(name=transfer['team1']).first()
                else:
                    team = Team.query.filter_by(name=transfer['team2']).first()

                team_to = transfer['team1']
                team_from = transfer['team2']

                if transfer['direction'] == 'out':
                    team_to = transfer['team2']
                    team_from = transfer['team1']

                player = Player.query.filter_by(name=transfer['name']).first()
                if player is None:
                    player = get_or_create(db.session, Player,
                                           name=transfer['name'],
                                           transferred_out=True,
                                           current_team=team.team_id)

                transfer_date = datetime.strptime(transfer['date'], '%d %B %Y')
                end_year = transfer_date.year

                # The season is scheduled to finish on May (Jun, Jul contingency)
                season_end = datetime.strptime('31 Jul {}'.format(transfer_date.year), '%d %b %Y')
                if transfer_date > season_end:
                    end_year = transfer_date.year + 1
                season = Season.query.filter(sqlalchemy.extract('year', Season.end_year) == end_year).first()

                get_or_create(db.session, Transfer,
                              player=player.player_id,
                              transfer_window_end=transfer_date,
                              transfer_from=team_from,
                              transfer_to=team_to,
                              details=transfer['details'],
                              season=season.season_id)

    return render_template(STATIC_TEMPLATE, message='Parse transfers .. OK! Next: Parse transfers')


@app.route('/fixtures', methods=['GET'])
def parse_fixtures():

    missing = ''
    for src in glob.glob(OLD_FIXTURES):

        with open(src) as outfile:
            fixtures = json.load(outfile)

        for fixture in fixtures:

            match_date = fixture['date']

            kickoff_datetime = "{} {}".format(match_date, fixture['details']['kick_off'])
            kickoff = datetime.strptime(kickoff_datetime, '%A %d %B %Y %H:%M')

            # The season is scheduled to finish on May
            season_end = datetime.strptime('31 Jul {}'.format(kickoff.year), '%d %b %Y')
            if kickoff > season_end:
                end_year = kickoff.year + 1
            else:
                end_year = kickoff.year

            season = Season.query.filter(sqlalchemy.extract('year', Season.end_year) == end_year).first()
            home_team = Team.query.filter_by(name_short=fixture['home_team']).first()
            away_team = Team.query.filter_by(name_short=fixture['away_team']).first()
            referee = Referee.query.filter_by(name=fixture['details']['referee']).first()

            match = None
            try:
                match = get_or_create(db.session, Match,
                                      home_team=home_team.team_id,
                                      away_team=away_team.team_id,
                                      kickoff=kickoff,
                                      season=season.season_id,
                                      main_referee=referee.referee_id)
            except AttributeError:
                missing += '<br>{} {} {} {}'.format(fixture['details']['referee'],
                                                    fixture['home_team'],
                                                    fixture['away_team'],
                                                    fixture['date'])

            for event in (fixture['details']['goals']):

                player_id = None
                try:
                    player = Player.query.filter_by(name=event['scorer']).first()
                    player_id = player.player_id
                except AttributeError:
                    missing += '<br>{} {} {} {}'.format(event['scorer'],
                                                        fixture['home_team'],
                                                        fixture['away_team'],
                                                        fixture['date'])

                own_goal = False
                if 'true' in event['own_goal']:
                    own_goal = True

                assist = None
                try:
                    player_assist = Player.query.filter_by(name=event['assist']).first()
                    assist = player_assist.player_id
                except KeyError:
                    pass

                except AttributeError:

                    missing += '<br>{} {} {} {}'.format(event['assist'],
                                                        fixture['home_team'],
                                                        fixture['away_team'],
                                                        fixture['date'])
                extra_time = None
                try:
                    extra_time = event['additional']
                except KeyError:
                    pass

                penalty = False
                if assist is None:
                    if own_goal:
                        penalty = False

                get_or_create(db.session,
                              Goal,
                              match=match.match_id,
                              penalty=penalty,
                              own_goal=own_goal,
                              player=player_id,
                              assist_player=assist,
                              extra_time=extra_time,
                              minute=event['minute'])

            for event in (fixture['details']['cards']):

                player_id = None
                try:
                    player = Player.query.filter_by(name=event['player']).first()
                    player_id = player.player_id
                except AttributeError:
                    missing += '<br>{} {} {} {}'.format(event['player'],
                                                        fixture['home_team'],
                                                        fixture['away_team'],
                                                        fixture['date'])

                extra_time = 0
                try:
                    extra_time = event['additional']
                except KeyError:
                    pass

                yellow = True
                if event['card'] == 'red':
                    yellow = False

                get_or_create(db.session, Card,
                              match=match.match_id,
                              yellow=yellow,
                              player=player_id,
                              extra_time=extra_time,
                              minute=event['minute'])

            for event in (fixture['details']['substitutions']):

                player_out = None
                try:
                    player = Player.query.filter_by(name=event['out']).first()
                    player_out = player.player_id
                except AttributeError:
                    missing += '<br>{} {} {} {}'.format(event['out'],
                                                        fixture['home_team'],
                                                        fixture['away_team'],
                                                        fixture['date'])

                player_in = None
                try:
                    player = Player.query.filter_by(name=event['in']).first()
                    player_in = player.player_id
                except KeyError:
                    pass

                except AttributeError:
                    missing += '<br>{} {} {} {}'.format(event['in'],
                                                        fixture['home_team'],
                                                        fixture['away_team'],
                                                        fixture['date'])

                extra_time = 0
                try:
                    extra_time = event['additional']
                except KeyError:
                    pass

                get_or_create(db.session,
                              Substitution,
                              match=match.match_id,
                              player_out=player_out,
                              player_in=player_in,
                              extra_time=extra_time,
                              minute=event['minute'])
    if len(missing) > 0:
        return missing

    return render_template(STATIC_TEMPLATE, message='Parse fixtures .. OK! Next: Parse new fixtures')


@app.route('/newfixtures', methods=['GET'])
def parse_new_fixtures():



    game_count = 0
    missing = ''
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

                season = Season.query.filter(sqlalchemy.extract('year', Season.end_year) == end_year).first()
                home_team = Team.query.filter_by(name_short=fixture['home_team']).first()
                away_team = Team.query.filter_by(name_short=fixture['away_team']).first()
                referee = Referee.query.filter_by(name=fixture['details']['referee']).first()

                match = None
                try:
                    match = get_or_create(db.session,
                                          Match,
                                          home_team=home_team.team_id,
                                          away_team=away_team.team_id,
                                          kickoff=kickoff,
                                          season=season.season_id,
                                          main_referee=referee.referee_id)

                    game_count += 1

                except AttributeError:
                    missing += '<br>{} {} {} {}'.format(fixture['details']['referee'],
                                                        fixture['home_team'],
                                                        fixture['away_team'],
                                                        fixture['date'])

                for event in (fixture['details']['goals']):

                    player = Player.query.filter_by(name=event['scorer']).first()
                    own_goal = False
                    if 'true' in event['own_goal']:
                        own_goal = True

                    assist = None
                    try:
                        player_assist = Player.query.filter_by(name=event['assist']).first()
                        assist = player_assist.player_id
                    except KeyError:
                        pass

                    except AttributeError:

                        missing += '<br>{} {} {} {}'.format(event['assist'],
                                                            fixture['home_team'],
                                                            fixture['away_team'],
                                                            fixture['date'])

                    extra_time = 0
                    try:
                        extra_time = event['additional']
                    except KeyError:
                        pass

                    penalty = False
                    if assist is None:
                        if own_goal:
                            penalty = False

                    get_or_create(db.session, Goal,
                                  match=match.match_id,
                                  penalty=penalty,
                                  own_goal=own_goal,
                                  player=player.player_id,
                                  assist_player=assist,
                                  extra_time=extra_time,
                                  minute=event['minute'])

                for event in (fixture['details']['cards']):

                    player = Player.query.filter_by(name=event['player']).first()
                    extra_time = 0
                    try:
                        extra_time = event['additional']
                    except KeyError:
                        pass

                    yellow = True
                    if event['card'] == 'red':
                        yellow = False

                    get_or_create(db.session, Card,
                                  match=match.match_id,
                                  yellow=yellow,
                                  player=player.player_id,
                                  extra_time=extra_time,
                                  minute=event['minute'])

                for event in (fixture['details']['substitutions']):

                    player_out = None
                    try:
                        player = Player.query.filter_by(name=event['out']).first()
                        player_out = player.player_id
                    except AttributeError:
                        missing += '<br>{} {} {} {}'.format(event['out'],
                                                            fixture['home_team'],
                                                            fixture['away_team'],
                                                            fixture['date'])

                    player_in = None
                    try:
                        player = Player.query.filter_by(name=event['in']).first()
                        player_in = player.player_id
                    except KeyError:
                        pass

                    except AttributeError:
                        missing += '<br>{} {} {} {}'.format(event['in'],
                                                            fixture['home_team'],
                                                            fixture['away_team'],
                                                            fixture['date'])

                    extra_time = 0
                    try:
                        extra_time = event['additional']
                    except KeyError:
                        pass

                    get_or_create(db.session, Substitution,
                                  match=match.match_id,
                                  player_out=player_out,
                                  player_in=player_in,
                                  extra_time=extra_time,
                                  minute=event['minute'])

    return render_template(STATIC_TEMPLATE, message='Parse new fixtures.. OK! Next: Statistics')


@app.route('/statistics', methods=['GET'])
def parse_statistics():
    """
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

    urllib.request.urlretrieve(STATISTICS_URL, STATISTICS)
    csv_file = open(STATISTICS, 'r')
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

            home_team = Team.query.filter_by(name_short=row["HomeTeam"]).first()
            away_team = Team.query.filter_by(name_short=row["AwayTeam"]).first()

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
            match = Match.query.filter(Match.home_team == home_team_id)\
                               .filter(Match.away_team == away_team_id)\
                               .filter(kickoff_casted == match_day_casted).first()
            try:
                match_id = match.match_id
            except AttributeError:
                return '[M] {} vs {} on {}'.format(row["HomeTeam"], row["AwayTeam"], row['Date'])

            result = {'H': 1, 'A': 2, 'D': 3}

            get_or_create(db.session, MatchStatistics,
                          match=match_id,
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
    return render_template(STATIC_TEMPLATE, message='Parse statistics .. OK! Process complete')
