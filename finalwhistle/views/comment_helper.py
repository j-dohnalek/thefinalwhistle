from finalwhistle.models.comment import *
from finalwhistle.views.misc_helper import strip_tags
from sqlalchemy import desc, asc
from flask import request
from finalwhistle import db
from flask_login import current_user
from finalwhistle.models.user import User


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st',2: 'nd',3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def handle_comment_post(cls):

    if request.method == 'POST':

        parent = 0
        message = strip_tags(request.form['message'].strip())
        page_id = strip_tags(request.form['page_id'].strip())

        if len(request.form) == 3:
            parent = strip_tags(request.form['parent'].strip())

        if len(message) < 2:
            return dict(error='The comment is too short', success=None)

        session = db.session

        if cls is ArticleComment:
            new_message = ArticleComment(body=message, article_id=page_id, posted_by=current_user.id, parent_id=parent)
            session.add(new_message)
            session.commit()
        else:
            new_message = MatchComment(body=message, match_id=page_id, posted_by=current_user.id, parent_id=parent)
            session.add(new_message)
            session.commit()

        return dict(error=None, success='Comment posted successfully')

    return dict(error=None, success=None)


def get_comments(session, id):
    """
    Fetch all comments
    :param session: ArticleComment or MatchComment class
    :param id: page_id
    :return: dict
    """
    parent = None

    if session is ArticleComment:
        # Try to fetch comment for article
        parents = session.query.filter(session.article_id == id)\
            .filter(session.parent_id == 0).order_by(desc(session.id)).all()
    else:
        # Otherwise, fetch comments for match
        parents = session.query.filter(session.match_id == id) \
            .filter(session.parent_id == 0).order_by(desc(session.id)).all()

    comments = []

    for parent in parents:

        user = User.query.filter(User.id == parent.posted_by).first()

        parent_comment = {
            'id': parent.id,
            'username': user.username,
            'body': parent.body,
            'posted_at': custom_strftime('%B {S}, %Y', parent.posted_at),
            'children': []
        }

        children = session.query.filter_by(parent_id=parent.id).order_by(asc(session.id)).all()
        for child in children:
            user = User.query.filter(User.id == parent.posted_by).first()

            child_comment = {
                'username': user.username,
                'body': child.body,
                'posted_at': custom_strftime('%B {S}, %Y', child.posted_at)
            }
            parent_comment['children'].append(child_comment)

        comments.append(parent_comment)

    return comments

