"""
Small miscellaneous functions which may be of use in various places
"""
from functools import wraps

from flask import url_for, redirect, flash
from flask_login import current_user


def new_uuid():
    import uuid
    return str(uuid.uuid4())


def remove_html_tags(text):
    """
    Strip html tags from string, see [1]
    [1] https://tutorialedge.net/python/removing-html-from-string/
    :param text: string
    :return: input string stripped of html tags
    """
    import re
    rx = re.compile(r'<[^>]+>')
    return rx.sub('', text)


def require_editor(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_editor:
            flash('You do not have access to that page')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function


def require_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_superuser:
            flash('You do not have access to that page')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function