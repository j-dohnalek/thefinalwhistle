from finalwhistle import db


class User(db.Model):
    """
    The User class must implement certain methods for Flask-Login compatibility [1]
    [1]: https://flask-login.readthedocs.io/en/latest/#your-user-class
    """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


    def is_authenticated(self):
        """
        This property should return True if the user is authenticated, i.e. they have provided valid credentials.
        (Only authenticated users will fulfill the criteria of login_required.) [1]
        [1]: https://flask-login.readthedocs.io/en/latest/#your-user-class
        """
        return False


    def is_active(self):
        """
        This property should return True if this is an active user - in addition to being authenticated,
        they also have activated their account, not been suspended, or any condition your application has for
        rejecting an account. Inactive accounts may not log in (without being forced of course).[1]
        [1]: https://flask-login.readthedocs.io/en/latest/#your-user-class
        """
        return False


    def is_anonymous(self):
        """
        This property should return True if this is an anonymous (guest) user. (Actual users should return False instead.) [1]
        [1]: https://flask-login.readthedocs.io/en/latest/#your-user-class
        """
        return False


    def get_id(self):
        """
        This method must return a unicode that uniquely identifies this user, and can be used to load the user from
        the user_loader callback. Note that this must be a unicode - if the ID is natively an int or some other type,
        you will need to convert it to unicode. [1]
        [1]: https://flask-login.readthedocs.io/en/latest/#your-user-class
        """
        return None