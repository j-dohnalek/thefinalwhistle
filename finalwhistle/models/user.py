"""
Database models for users/accounts
"""
from finalwhistle import db, bcrypt


class User(db.Model):
    """
    The User class must implement certain methods for Flask-Login compatibility [1]
    [1]: https://flask-login.readthedocs.io/en/latest/#your-user-class

    The blocked/restricted fields in the logical diagram could be move to a security group which
    can be expanded to limit access to the commenting system and basic account actions (e.g. logging in).
    If we want to keep the functionality of recording the dates the user was moved into the group, we'd
    need a new table to record instances of a user's group changing

    Passwords are safely stored via Flask-BCrypt [1]

    [1] https://flask-bcrypt.readthedocs.io/en/latest/
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(60), nullable=False, unique=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    pw_hash = db.Column(db.Binary(60), nullable=False, unique=True)
    registered_date = db.Column(db.DateTime, nullable=False)
    last_login = db.Column(db.DateTime)
    supported_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    supported_team = db.relationship('Team')
    usergroup_id = db.Column(db.Integer, db.ForeignKey('usergroups.id'))
    usergroup = db.relationship('SecurityGroup')

    def hash_password(self, password):
        """
        Generates hash of the password

        In Python 3, you need to use decode(‘utf-8’) on generate_password_hash() [1]

        [1] https://flask-bcrypt.readthedocs.io/en/latest/#usage
        :param password: Supplied password
        :return: Hash of the password
        """
        return bcrypt.generate_password_hash(password).decode('utf-8')

    def password_valid(self, password):
        """
        Checks if supplied password is valid for the account

        :param password: Supplied password
        :return: True if password is correct
        """
        return bcrypt.check_password_hash(self.pw_hash, password)

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
        This property should return True if this is an anonymous (guest)
        user. (Actual users should return False instead.) [1]
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
