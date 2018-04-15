from server import app
from flask import render_template


from views.public_helper import get_league_table, get_all_teams, get_team_information

#####################
# data view routing #
#####################


@app.route('/', methods=['GET'])
def index():
    return 'OK'


@app.route('/matches', methods=['GET'])
def matches_overview():
    return 'matches overview'


@app.route('/matches/<id>', methods=['GET'])
def match_page(id):
    return 'match page {id}'


@app.route('/players', methods=['GET'])
def players_overview():
    return 'players overview'


@app.route('/players/<id>', methods=['GET'])
def player_page(id):
    return 'player page {id}'


@app.route('/news', methods=['GET'])
def news_overview():
    return 'news overview'


@app.route('/news/<id>', methods=['GET'])
def news_page(id):
    return 'news page {id}'


@app.route('/teams', methods=['GET'])
def teams_overview():
    return render_template('teams.html', data=get_all_teams())


@app.route('/teams/<id>', methods=['GET'])
def team_page(id):
    return render_template('team.html', data=get_team_information(id))


@app.route('/table', methods=['GET'])
def league_table():
    return render_template('league_table.html', data=get_league_table())

