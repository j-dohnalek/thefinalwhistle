from flask import render_template
from flask_login import login_required, login_user, logout_user

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