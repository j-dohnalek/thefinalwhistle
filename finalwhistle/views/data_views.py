from flask import render_template

from finalwhistle import app

from finalwhistle.views.data_views_helper import list_all_matches, get_match_information, STATS, get_all_players, \
    get_player_information, get_all_teams, get_team_information, get_league_table

#####################
# data view routing #
#####################
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


@app.route('/teams', methods=['GET'])
def teams_overview():
    return render_template('teams.html', data=get_all_teams())


@app.route('/teams/<id>', methods=['GET'])
def team_page(id):
    return render_template('team.html', team=get_team_information(id))


@app.route('/league-table', methods=['GET'])
def league_table():
    return render_template('league_table.html', table=get_league_table())


@app.route('/news', methods=['GET'])
def news_overview():
    return render_template('news.html')


@app.route('/news/<id>', methods=['GET'])
def news_page(id):
    return f'news page {id}'
