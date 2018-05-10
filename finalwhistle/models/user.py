"""
Database models for users/accounts
"""
import hashlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import validates

from finalwhistle import db, bcrypt, app
from finalwhistle.helpers import new_uuid
from sqlalchemy.sql import func
from flask_login import UserMixin
from datetime import datetime, timedelta

from finalwhistle.mailing import send_registration_email


class UserNotActivated(Exception):
    pass


class UserIsBlocked(Exception):
    pass


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
        if not user.activated:
            raise UserNotActivated
        if user.is_blocked:
            raise UserIsBlocked
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

    """
    if 'block' in mode and (new_state or not new_state):
        user = User.query.filter_by(id=id).first()
        user.blocked = new_state
        db.session.commit()
        return user
    """

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
        return new_user
    except SQLAlchemyError:
        print('something went wrong when making a new account!')
    return None


def validate_password(password):
    import re
    if not re.match(r'[A-Za-z0-9]{8,}', password):
        raise AssertionError('Invalid password')
    return password


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
    registered_date = db.Column(db.DateTime, nullable=False, server_default=func.now())
    last_login = db.Column(db.DateTime, nullable=False, server_default=func.now())
    # Accounts must be activated before they can be used
    activated = db.Column(db.Boolean, nullable=False, default=False)
    # Access token is used for email confirmation and password resets
    access_token = db.Column(db.String, nullable=True)
    access_token_expires_at = db.Column(db.DateTime, nullable=True)
    supported_team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=True)
    supported_team = db.relationship('Team')
    # permissions
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

    # https://stackoverflow.com/questions/8256715/simple-validation-with-sqlalchemy
    @validates('email')
    def validate_email(self, key, address):
        if '@' not in address:
            raise AssertionError('Invalid email')
        return address

    def __init__(self, email, username, password, name):
        """
        Creates a new user in the database
        :param email:
        :param username:
        :param password:
        """
        if validate_password(password):
            self.email = email
            self.username = username
            self.pw_hash = hash_password(password)
            self.real_name = name
            self.new_token()
            send_registration_email(email, self.access_token)

    def __repr__(self):
        return f'<User> {self.id}: {self.email}'

    def new_token(self, reset=False):
        # Set normally
        if not reset:
            hash = hashlib.md5()
            hash.update(str(self.pw_hash).encode('utf-8'))
            hash.update(str(self.email).encode('utf-8'))
            self.access_token = hash.hexdigest()
            self.access_token_expires_at = datetime.now() + timedelta(days=1)
        # Reset to empty
        else:
            self.access_token = None
            self.access_token_expires_at = None
        db.session.add(self)
        db.session.commit()

    def password_valid(self, password):
        """
        Checks if supplied password is valid for the account
        :param password:
        :return: True if password is correct
        """
        return bcrypt.check_password_hash(self.pw_hash, password)

    def is_active(self):
        return self.activated

    def activate_account(self, token):
        """
        :return: True if account is successfully activated
        """
        # Return false if trying to activate an already active account
        if self.activated:
            return False
        # Verify token sent to user in email
        if token == str(self.access_token):
            self.activated = True
            self.new_token(reset=True)
            db.session.add(self)
            db.session.commit()
        return self.activated

    def account_disabled(self):
        """
        :return: True if account does not have function to login
        """
        return self.is_blocked

    def verify_activation_token(self, token):
        return self.activation_token == token

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
        self.last_login = datetime.now()
        db.session.add(self)
        db.session.commit()

