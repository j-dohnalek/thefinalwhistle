from server import app
from server import db
from football import Referee, ClubStaff, League, Season, Stadium, Team
from football import ClubStaff, Player, Transfer
from football import Match, Card, Goal, Substitution
from misc import get_or_create, record_exists

import json
from datetime import datetime
import glob
import sqlalchemy

#################################

REFEREE_JSON = 'json/list_of_referees.json'
STADIUM_JSON = 'json/list_of_stadiums.json'
CLUB_STAFF_JSON = 'json/list_of_managers.json'

################################


@app.route('/', methods=['GET'])
def index():
    return 'It Works! <a href="./create">Create</a>'


@app.route('/create', methods=['GET'])
def create():
    db.create_all(app=app)
    return 'Database created! <a href="./referee">Next</a>'


@app.route('/referee', methods=['GET'])
def parse_referee():

    with open(REFEREE_JSON) as outfile:
        referees = json.load(outfile)
        list_of_referees = referees[0]['referees']

    for referee in list_of_referees:
        get_or_create(db.session, Referee, name=referee)

    return 'Referees Parsed OK! <a href="./league">Next</a>'


@app.route('/league', methods=['GET'])
def parse_league():
    get_or_create(db.session, League, name='Premier League')

    return 'League Parsed OK <a href="./season">Next</a>'


@app.route('/season', methods=['GET'])
def parse_season():
    s = '2018-01-01'
    date_format = '%Y-%m-%d'
    date = datetime.strptime(s, date_format)
    get_or_create(db.session, Season, end_year=date)

    return 'Season Parsed OK <a href="./stadiums">Next</a>'


@app.route('/stadiums', methods=['GET'])
def parse_stadiums():

    with open(STADIUM_JSON) as outfile:
        stadiums = json.load(outfile)
    for stadium in stadiums:
        get_or_create(db.session, Stadium, name=stadium['stadium'])

    return 'Stadiums Parsed OK! <a href="./teams">Next</a>'


@app.route('/teams', methods=['GET'])
def parse_teams():
    with open(STADIUM_JSON) as outfile:
        clubs = json.load(outfile)

    for club in clubs:

        stadium = Stadium.query.filter_by(name=club['stadium']).first()
        league = League.query.filter_by(name='Premier League').first()
        get_or_create(db.session, Team, name=club['club'], name_short=club['club_short'],
                      stadium=stadium.stadium_id, league=league.league_id)

    return 'Teams Parsed OK! <a href="./clubstaff">Next</a>'


@app.route('/clubstaff', methods=['GET'])
def parse_club_staff():

    with open(CLUB_STAFF_JSON) as outfile:
        clubs = json.load(outfile)

    for club in clubs:
        team = Team.query.filter(Team.name.like("%" + club['club'] + "%")).first()
        for manager in club['managers']:
            get_or_create(db.session, ClubStaff, team=team.team_id, name=manager, role='manager')

    return 'ClubStaff Parsed OK! <a href="./players">Next</a>'


@app.route('/players', methods=['GET'])
def parse_players():

    for src in glob.glob("json/players/*.json"):

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
                                  dob=date
                    )

    return 'Players Parsed OK! ! <a href="./transfers">Next</a>'


@app.route('/transfers', methods=['GET'])
def parse_transfers():

    for src in glob.glob("json/transfers/*.json"):
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
                    player = get_or_create(db.session, Player, name=transfer['name'], transferred_out=True, current_team=team.team_id)

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

    return 'Transfers parse OK <a href="./fixtures">Next</a>'


@app.route('/fixtures', methods=['GET'])
def parse_fixtures():

    game_count = 0
    missing = ''
    for src in glob.glob("json/fixtures/*.json"):

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

            season = Season.query.filter(sqlalchemy.extract('year', Season.end_year)==end_year).first()
            home_team = Team.query.filter_by(name_short=fixture['home_team']).first()
            away_team = Team.query.filter_by(name_short=fixture['away_team']).first()
            referee = Referee.query.filter_by(name=fixture['details']['referee']).first()

            try:
                match = get_or_create(db.session, Match,
                              home_team=home_team.team_id,
                              away_team=away_team.team_id,
                              kickoff=kickoff,
                              season=season.season_id,
                              main_referee=referee.referee_id)
            except AttributeError:
                missing += '<br>{} {} {} {}'.format(fixture['details']['referee'], fixture['home_team'], fixture['away_team'], fixture['date'])

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

    return 'Fixtures Parsed OK {}'.format(missing)
