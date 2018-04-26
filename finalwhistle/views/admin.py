from flask import render_template
from flask_login import login_required, login_user, logout_user
from finalwhistle.data_collection.analytics.access_token import get_access_token

from finalwhistle import app

@app.route('/admin', methods=['GET'])
@login_required
def admin_overview():
    return render_template('admin/index.html')

@app.route('/admin/articles/new', methods=['GET'])
@login_required
def new_article():
    return render_template('admin/new_article.html')

@app.route('/admin/articles', methods=['GET'])
@login_required
def articles_overview():
    return render_template('admin/articles.html')

@app.route('/admin/stats', methods=['GET'])
@login_required
def analytics_overview():
    return render_template('admin/stats.html', token=get_access_token())