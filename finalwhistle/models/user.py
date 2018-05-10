"""
Database models for users/accounts
"""
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import validates

from finalwhistle import db, bcrypt, app
from finalwhistle.helpers import new_uuid
from sqlalchemy.sql import func
from flask_login import UserMixin
import datetime


def hash_password(password):
    """
    Generates hash of the password
    :param password: Supplied password
       :return: Hash of the password
    """
    from finalwhistle import bcrypt
    return bcrypt.generate_password_hash(password)


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


def attempt_login(email, password):
    """
    Check validity of supplied email/password
    :param email: email address
    :param password: password
    :return: user object if password correct, else None
    """
    user = get_user_by_email(email)
    # The user has to be object
    if user is not None:
        if user.password_valid(password):
            user.update_last_login()
            return user
    return None


def update_privilege(id, mode, new_state):
    """
    Update user privilege
    :param id: user id
    :param mode:
    :param new_state:
    :return:
    """
    try:
        if User.query.filter(User.id == id).first() is None:
            return None
    except Exception:
        return None

    if 'editor' in mode and (new_state or not new_state):
        user = User.query.filter_by(id=id).first()
        user.is_editor = new_state
        db.session.commit()
        return user

    if 'block' in mode and (new_state or not new_state):
        user = User.query.filter_by(id=id).first()
        user.is_blocked = new_state
        db.session.commit()
        return user

    return None


def create_new_user(email, username, password, name):
    """
    Create and commit a new User object
    :param email:       new user email
    :param username:    new user username
    :param password:    new user password
    :return:            new user if created, otherwise None
    """
    try:
        new_user = User(email=email,
                        username=username,
                        password=password,
                        name=name)

        db.session.add(new_user)
        db.session.commit()
        # TODO: send activation email
        return new_user
    except SQLAlchemyError:
        print('something went wrong when making a new account!')
    return None


class User(UserMixin, db.Model):
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
    real_name = db.Column(db.String(60))
    pw_hash = db.Column(db.Binary(60), nullable=False, unique=True)
    # Accounts must be activated before they can be used
    activated = db.Column(db.Boolean, nullable=False, default=False)
    # The user is emailed the activation token which can be entered by attempting to login or by clicking
    # a link emailed to them
    registered_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    last_login = db.Column(db.DateTime, nullable=False, server_default=func.now())
    # Access token is used for password reset requests and the 'remember me' function
    access_token = db.Column(db.String, nullable=True)
    access_token_expires_at = db.Column(db.DateTime, nullable=True)
    supported_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=True)
    supported_team = db.relationship('Team')
    #usergroup_id = db.Column(db.Integer, db.ForeignKey('usergroups.id'), nullable=True)
    #usergroup = db.relationship('UserGroup')
    is_superuser = db.Column(db.Boolean, nullable=False, default=False)
    is_editor = db.Column(db.Boolean, nullable=False, default=False)
    is_blocked = db.Column(db.Boolean, nullable=False, default=False)

    @validates('supported_team_id')
    def validate_supported_team_id(self, key, team_id):
        from finalwhistle.models.football import Team
        max = len(Team.query.all())
        if team_id < 1 or team_id > max:
            raise ValueError('Tried to set supported_team_id outside range ')
        return team_id

    def __init__(self, email, username, password, name):
        """
        Creates a new user in the database
        :param email:
        :param username:
        :param password:
        """
        self.email = email
        self.username = username
        self.pw_hash = hash_password(password)
        self.real_name = name
        # TODO: send account activation email

    def __repr__(self):
        return f'<User> {self.id}: {self.email}'

    def password_valid(self, password):
        """
        Checks if supplied password is valid for the account
        :param password:
        :return: True if password is correct
        """
        return bcrypt.check_password_hash(self.pw_hash, password)

    def account_activated(self):
        return self.activated is True

    def activate_account(self):
        """
        :return: True if account is successfully activated
        """
        # Return false if trying to activate an already active account
        if self.account_activated():
            return False
        self.activated = True
        return self.activated

    def account_disabled(self):
        """
        :return: True if account does not have function to login granted by their usergroup
        """
        return False

    def verify_activation_token(self, token):
        return self.activation_token == token

    @staticmethod
    def attempt_login(email, password):
        """
        Attempts to login with a provided email and password
        :param email:
        :param password:
        :return:    User object associated with the provided email if password is correct, otherwise None
        """
        user = get_user_by_email(email)
        if user.password_valid(password):
            user.last_login = func.now()
            return user
        else:
            # can implement failed login attempt tracker here
            pass
        return None

    def set_real_name(self, name):
        try:
            self.real_name = name
            db.session.add(self)
            db.session.commit()
        except:
            pass
        return False

    def set_supported_team(self, team_id):
        try:
            team_id = int(team_id)
            if team_id == self.supported_team_id:
                return False
            self.supported_team_id = team_id
            db.session.add(self)
            db.session.commit()
            return True
        except (ValueError, TypeError) as e:
            print('tried to set supported team to something which couldn\'t be cast to int')
            print(e)
        return False

    def set_password(self, password):
        try:
            self.pw_hash = hash_password(password)
            db.session.add(self)
            db.session.commit()
            return True
        except:
            return False

    def update_last_login(self):
        self.last_login = datetime.datetime.now()
        db.session.add(self)
        db.session.commit()

