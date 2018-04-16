from server import app
from flask import render_template


from views.public_helper import get_league_table, get_all_teams, get_team_information
from views.public_helper import get_all_players, get_player_information, list_all_matches
from views.public_helper import get_match_information
from views.public_helper import STATS

#####################
# data view routing #
#####################


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


@app.route('/matches', methods=['GET'])
def matches_overview():
    return render_template('matches.html', data=list_all_matches())


@app.route('/matches/<id>', methods=['GET'])
def match_page(id):
    return render_template('match.html', match=get_match_information(id), statistics=STATS)


@app.route('/players', methods=['GET'])
def players_overview():
    return render_template('players.html', data=get_all_players())


@app.route('/players/<id>', methods=['GET'])
def player_page(id):
    return render_template('player.html', data=get_player_information(id))


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
    return render_template('team.html', team=get_team_information(id))


@app.route('/table', methods=['GET'])
def league_table():
    return render_template('league_table.html', table=get_league_table())

