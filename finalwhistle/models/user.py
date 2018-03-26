"""
Database models for users/accounts
"""
from finalwhistle import db, bcrypt
from finalwhistle.helpers import new_uuid
from sqlalchemy.sql import func

def hash_password(password):
    """
    Generates hash of the password

    In Python 3, you need to use decode(‘utf-8’) on generate_password_hash() [1]

    [1] https://flask-bcrypt.readthedocs.io/en/latest/#usage
    :param password: Supplied password
    :return: Hash of the password
    """
    from finalwhistle import bcrypt
    return bcrypt.generate_password_hash(password).decode('utf-8')


def user_from_email(email):
    return User.query.filter_by(email=email).first()


class User(db.Model):
    """
    The blocked/restricted fields in the logical diagram could be move to a security group which
    can be expanded to limit access to the commenting system and basic account actions (e.g. logging in).
    If we want to keep the functionality of recording the dates the user was moved into the group, we'd
    need a new table to record instances of a user's group changing

    Passwords are safely stored via Flask-BCrypt [1]

    [1]: https://flask-bcrypt.readthedocs.io/en/latest/
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(60), nullable=False, unique=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    pw_hash = db.Column(db.Binary(60), nullable=False, unique=True)
    # Accounts must be activated before they can be used
    activated = db.Column(db.Boolean, nullable=False, default=False)
    # The user is emailed the activation token which can be entered by attempting to login or by clicking
    # a link emailed to them
    activation_token = db.Column(db.String, nullable=False, default=new_uuid)
    registered_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    last_login = db.Column(db.DateTime, nullable=False, server_default=func.now())
    supported_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=True)
    supported_team = db.relationship('Team')
    usergroup_id = db.Column(db.Integer, db.ForeignKey('usergroups.id'), nullable=True)
    usergroup = db.relationship('UserGroup')
    # Access token is used for password reset requests and the 'remember me' function
    access_token = db.Column(db.String, nullable=False, default=new_uuid)
    access_token_expires_at = db.Column(db.DateTime, nullable=False)

    def __init__(self, email, username, password):
        """
        Creates a new user in the database
        :param email:
        :param username:
        :param password:
        """
        self.email = email
        self.username = username
        self.pw_hash = hash_password(password)
        # TODO: send account activation email

    def password_valid(self, password):
        """
        Checks if supplied password is valid for the account
        :param password:
        :return: True if password is correct
        """
        return bcrypt.check_password_hash(self.pw_hash, password)

    def activate_account(self):
        """

        :return: True if account has just been activated
        """
        if self.activated is not False:
            return False


    def activation_token_valid(self, token):
        return self.activation_token == token

    @staticmethod
    def attempt_login(email, password):
        """
        Attempts to login with a provided email and password
        :param email:
        :param password:
        :return: User object associated with the provided email if password is correct, otherwise None
        """
        user = user_from_email(email)
        if user.password_valid(password):
            return user
        else:
            # can implement failed login attempt tracker here
            pass
        return None

