from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from finalwhistle.data_collection.analytics.access_token import get_access_token

from finalwhistle import app
from finalwhistle.models.article import create_new_article

from finalwhistle.models.user import User

from flask import request

@app.route('/admin', methods=['GET'])
@login_required
def admin_overview():
    return render_template('admin/index.html', token=get_access_token())

@app.route('/admin/users', methods=['GET'])
@login_required
def users_overview():
    return render_template('admin/users.html', users=User.query.all())

@app.route('/admin/articles/new', methods=['GET', 'POST'])
@login_required
def new_article():
    if request.method == 'POST':
        form = request.form
        title = form.get('title')
        body = form.get('body')
        if title is not None and body is not None:
            new_article = create_new_article(current_user.id, title, body)
            if new_article is not None:
                flash('Article posted!')
                return redirect(url_for('articles_overview'))
            else:
                flash('Article could not be posted - please inform an administrator')
                return redirect(url_for('new_article'))
    return render_template('admin/new_article.html')

@app.route('/admin/articles', methods=['GET'])
@login_required
def articles_overview():
    return render_template('admin/articles.html', token=get_access_token())

@app.route('/admin/stats', methods=['GET'])
@login_required
def analytics_overview():
    return render_template('admin/stats.html', token=get_access_token())