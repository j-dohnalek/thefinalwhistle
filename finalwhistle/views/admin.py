from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from finalwhistle.data_collection.analytics.access_token import get_access_token

from finalwhistle import app
from finalwhistle.models.article import create_new_article, update_existing_article

from finalwhistle.models.user import User, update_privilege
from finalwhistle.models.article import Article
from finalwhistle.models.contact import fetch_all_messages, delete_message

from flask import request

from helpers import require_admin, require_editor


@app.route('/admin', methods=['GET'])
@login_required
@require_editor
def admin_overview():
    return render_template('admin/index.html', token=get_access_token())


@app.route('/admin/users', methods=['GET'])
@login_required
@require_admin
def users_overview():
    if request.method == 'GET':
        editor = request.args.get('editor')
        not_editor = request.args.get('noteditor')
        blocked = request.args.get('block')
        not_blocked = request.args.get('unblock')

        try:
            if editor is not None:
                id = int(request.args.get('editor'))
                update_privilege(id, 'editor', True)
                return redirect(url_for('users_overview'))

            if not_editor is not None:
                id = int(request.args.get('noteditor'))
                update_privilege(id, 'editor', False)
                return redirect(url_for('users_overview'))

            if blocked is not None:
                id = int(request.args.get('block'))
                update_privilege(id, 'block', True)
                return redirect(url_for('users_overview'))

            if not_blocked is not None:
                id = int(request.args.get('unblock'))
                update_privilege(id, 'block', False)
                return redirect(url_for('users_overview'))

        except ValueError:
            pass
        except TypeError:
            pass

    return render_template('admin/users.html', users=User.query.all())


@app.route('/admin/articles/new', methods=['GET', 'POST'])
@login_required
@require_editor
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


@app.route('/admin/messages', methods=['GET'])
@login_required
@require_admin
def message_overview():
    messages = fetch_all_messages()
    if request.method == 'GET':
        try:
            id = int(request.args.get('delete'))
            messages = delete_message(id)
            return redirect(url_for('message_overview'))
        except ValueError:
            pass
        except TypeError:
            pass

    return render_template('admin/messages.html', messages=messages)


@app.route('/admin/articles/edit/<id>', methods=['GET', 'POST'])
@login_required
@require_editor
def edit_article(id):

    article = Article.query.filter(Article.id == id).first()

    if request.method == 'POST':
        form = request.form
        title = form.get('title')
        body = form.get('body')
        if title is not None and body is not None:
            article = update_existing_article(id, title, body)
            if article is not None:
                flash('Article Updated!')
                return redirect(url_for('edit_article', id=id))
            else:
                flash('Article could not be posted - please inform an administrator')
                return redirect(url_for('new_article'))

    return render_template('admin/edit_article.html', article=article)


@app.route('/admin/articles', methods=['GET'])
@login_required
@require_editor
def articles_overview():
    from finalwhistle.models.article import get_latest_news
    return render_template('admin/articles.html', token=get_access_token(), articles=get_latest_news())


@app.route('/admin/stats', methods=['GET'])
@login_required
@require_admin
def analytics_overview():
    return render_template('admin/stats.html', token=get_access_token())