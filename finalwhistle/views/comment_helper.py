from finalwhistle.models.comment import *
from finalwhistle.views.misc_helper import strip_tags
from sqlalchemy import desc, asc
from flask import request
from finalwhistle import db
from flask_login import current_user


def suffix(d):
    return 'th' if 11 <= d <= 13 else {1: 'st',2: 'nd',3: 'rd'}.get(d % 10, 'th')


def custom_strftime(format, t):
    return t.strftime(format).replace('{S}', str(t.day) + suffix(t.day))


def get_match_comments(id):
    """
    Fetch all comments per match id
    :param id: match id
    :return: dict
    """

    parents = MatchComment.query\
        .filter(MatchComment.match_id == id)\
        .filter(MatchComment.parent_id == 0)\
        .order_by(desc(MatchComment.id)).all()

    comments = []

    for parent in parents:

        parent_comment = {
            'id': parent.id,
            'body': parent.body,
            'posted_at': custom_strftime('%B {S}, %Y', parent.posted_at),
            'children': []
        }

        children = MatchComment.query.filter_by(parent_id=parent.id).order_by(asc(MatchComment.id)).all()
        for child in children:
            child_comment = {'body': child.body, 'posted_at': custom_strftime('%B {S}, %Y', child.posted_at)}
            parent_comment['children'].append(child_comment)
        comments.append(parent_comment)

    return comments


def handle_match_comment_reply():

    if request.method == 'POST':

        parent = 0
        message = strip_tags(request.form['message'].strip())
        match = strip_tags(request.form['match'].strip())

        if len(request.form) == 3:
            parent = strip_tags(request.form['parent'].strip())

        if len(message) < 2:
            return dict(error='The comment is too short', success=None)

        session = db.session
        new_message = MatchComment(body=message, match_id=match, posted_by=current_user.id, parent_id=parent)
        session.add(new_message)
        session.commit()

        return dict(error=None, success='Message posted successfully')

    return dict(error=None, success=None)

