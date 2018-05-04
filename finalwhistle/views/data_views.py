from finalwhistle.models.article import Article
from finalwhistle.models.comment import MatchComment, ArticleComment

from finalwhistle.models.user import User

from flask import render_template
from finalwhistle import app, db
from flask import redirect, url_for

from sqlalchemy import func

from finalwhistle.views.data_views_helper import list_all_matches, get_match_information, STATS, get_all_players, \
    get_player_information, get_all_teams, get_team_information, get_league_table, list_referees

from finalwhistle.views.statistics_helper import top_tens_statistic, get_team_comparison, get_player_comparison
from finalwhistle.views.comment_helper import get_comments, handle_comment_post


#####################
# data view routing #
#####################
@app.route('/matches', methods=['GET'])
def matches_overview():
    return render_template('matches.html', data=list_all_matches())


@app.route('/matches/<id>', methods=['GET', 'POST'])
def match_page(id):
    match_information = get_match_information(id)

    if match_information is None:
        return redirect(url_for('error_404'))

    confirmation = handle_comment_post(MatchComment)
    comments = get_comments(MatchComment, id)
    return render_template('match.html',
                           match_id=id,
                           match=match_information,
                           statistics=STATS,
                           comments=comments,
                           confirmation=confirmation)


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


@app.route('/news/<id>', methods=['GET', 'POST'])
def news_page(id):

    if Article.query.filter(Article.id == id).first() is None:
        return redirect(url_for('error_404'))

    confirmation = handle_comment_post(ArticleComment)
    comments = get_comments(ArticleComment, id)

    article = Article.query.filter(Article.id == id) \
        .join(User, User.id == Article.author_id) \
        .outerjoin(ArticleComment, ArticleComment.article_id == Article.id) \
        .add_columns(User.real_name,
                     Article.id,
                     Article.body,
                     Article.submitted_at,
                     Article.title,
                     Article.featured_image,
                     func.count(ArticleComment.id).label('comments')) \
        .group_by(Article.id).first()

    return render_template('news_post.html',
                           article=article,
                           article_id=id,
                           confirmation=confirmation,
                           comments=comments)


@app.route('/compare-teams', methods=['GET'])
def compare_teams():
    comparison = get_team_comparison()
    return render_template('compare_teams.html', teams=get_all_teams(), stats=comparison)


@app.route('/compare-players', methods=['GET'])
def compare_players():
    comparison = get_player_comparison()
    return render_template('compare_players.html', players=get_all_players(), stats=comparison)


@app.route('/top-tens', methods=['GET'])
def top_tens():
    return render_template('top_tens.html', statistics=top_tens_statistic())


@app.route('/referees', methods=['GET'])
def referee_overview():
    return render_template('referees.html', referees=list_referees())
