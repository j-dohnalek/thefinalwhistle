from flask import render_template

from finalwhistle import app
from flask import redirect, url_for


from finalwhistle.views.data_views_helper import list_all_matches, get_match_information, STATS, get_all_players, \
    get_player_information, get_all_teams, get_team_information, get_league_table, get_compare_teams

#####################
# data view routing #
#####################
@app.route('/matches', methods=['GET'])
def matches_overview():
    return render_template('matches.html', data=list_all_matches())


@app.route('/matches/<id>', methods=['GET'])
def match_page(id):
    match_information = get_match_information(id)

    if match_information is None:
        return redirect(url_for('error_404'))

    return render_template('match.html', match=match_information, statistics=STATS)


@app.route('/players', methods=['GET'])
def players_overview():
    return render_template('players.html', data=get_all_players())


@app.route('/players/<id>', methods=['GET'])
def player_page(id):
    player_information = get_player_information(id)

    if player_information is None:
        return redirect(url_for('error_404'))

    return render_template('player.html', data=player_information)


@app.route('/teams', methods=['GET'])
def teams_overview():
    return render_template('teams.html', data=get_all_teams())


@app.route('/teams/<id>', methods=['GET'])
def team_page(id):
    team_information = get_team_information(id)

    if team_information is None:
        return redirect(url_for('error_404'))

    return render_template('team.html', team=team_information)


@app.route('/league-table', methods=['GET'])
def league_table():
    return render_template('league_table.html', table=get_league_table())


@app.route('/news', methods=['GET'])
def news_overview():
    from finalwhistle.models.article import get_latest_news
    return render_template('news.html', news=get_latest_news())


@app.route('/news/<id>', methods=['GET'])
def news_page(id):
    return f'news page {id}'


@app.route('/compare/teams', methods=['GET', 'POST'])
def compare_teams():
    comparison = get_compare_teams()
    return render_template('compare_teams.html', teams=get_all_teams(), comparison=comparison)