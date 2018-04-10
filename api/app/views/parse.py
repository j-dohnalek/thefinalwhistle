from server import app
from server import db
from football import Referee, ClubStaff, League, Season, Stadium, Team
from football import ClubStaff, Player
from football import Match, Card, Goal, Substitution
from misc import get_or_create, record_exists

import json
import datetime
import glob

#################################

REFEREE_JSON = 'json/list_of_referees.json'
STADIUM_JSON = 'json/list_of_stadiums.json'
CLUB_STAFF_JSON = 'json/list_of_managers.json'

#################################


@app.route('/', methods=['GET'])
def index():
    return 'It Works!'


@app.route('/referee', methods=['GET'])
def parse_referee():

    with open(REFEREE_JSON) as outfile:
        referees = json.load(outfile)
        list_of_referees = referees[0]['referees']

    for referee in list_of_referees:
        get_or_create(db.session, Referee, name=referee)

    return 'Referees Parsed OK'


@app.route('/league', methods=['GET'])
def parse_league():
    get_or_create(db.session, League, name='Premier League')

    return 'League Parsed OK'


@app.route('/season', methods=['GET'])
def parse_season():
    s = '2018-01-01'
    date_format = '%Y-%m-%d'
    date = datetime.datetime.strptime(s, date_format)
    get_or_create(db.session, Season, end_year=date)

    return 'Season Parsed OK'


@app.route('/stadiums', methods=['GET'])
def parse_stadiums():

    with open(STADIUM_JSON) as outfile:
        stadiums = json.load(outfile)
    for stadium in stadiums:
        get_or_create(db.session, Stadium, name=stadium['stadium'])

    return 'Stadiums Parsed OK'


@app.route('/teams', methods=['GET'])
def parse_teams():
    with open(STADIUM_JSON) as outfile:
        clubs = json.load(outfile)

    for club in clubs:

        stadium = Stadium.query.filter_by(name=club['stadium']).first()
        league = League.query.filter_by(name='Premier League').first()
        get_or_create(db.session, Team, name=club['club'], name_short=club['club_short'],
                      stadium=stadium.stadium_id, league=league.league_id)

    return 'Stadiums Parsed OK'


@app.route('/clubstaff', methods=['GET'])
def parse_club_staff():

    with open(CLUB_STAFF_JSON) as outfile:
        clubs = json.load(outfile)

    for club in clubs:
        team = Team.query.filter(Team.name.like("%" + club['club'] + "%")).first()
        for manager in club['managers']:
            get_or_create(db.session, ClubStaff, team=team.team_id, name=manager, role='manager')

    return 'ClubStaff Parsed OK'


@app.route('/players', methods=['GET'])
def parse_players():

    for src in glob.glob("json/players/*.json"):

        with open(src) as outfile:
            players = json.load(outfile)

        for club in players:
            team = Team.query.filter_by(name=club['club']).first()
            for player in club['players']:

                date_format = '%d/%m/%Y'
                date = datetime.datetime.strptime(player['dob'], date_format)

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

    return 'ClubStaff Parsed OK'


@app.route('/fixtures', methods=['GET'])
def parse_fixtures():

    for src in glob.glob("json/fixtures/*.json"):

        with open(src) as outfile:
            match_day = json.load(outfile)

        match_date = match_day['date']

        for fixture in match_day['fixtures']:
            match_date + fixture['details']['kick_off']

            matchday = datetime.strptime(fixture['date'], '%A %d %B %Y %H:%M')

            home_team = Team.query.filter_by(short_name=fixture['home_team']).first()
            away_team = Team.query.filter_by(short_name=fixture['away_team']).first()

            get_or_create(db.session, Match,
                          home_team=home_team.team_id,
                          away_team=away_team.team_id,)




    return 'ClubStaff Parsed OK'
