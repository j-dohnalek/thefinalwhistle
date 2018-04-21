def get_user_by_email(email):
    """
    Get user object from email address
    :param email: email address
    :return: user object associated with supplied email
    """
    return User.query.filter_by(email=email).first()


def get_user_by_id(user_id):
    """
    Get user object from id. Required for flask-login functionality [1]
    [1]: https://flask-login.readthedocs.io/en/latest/#how-it-works
    :param id:
    :return:
    """
    return User.query.filter_by(id=user_id).first()