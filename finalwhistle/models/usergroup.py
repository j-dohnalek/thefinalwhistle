"""
Database models for permissions and security groups system
See [1] for explanation of 'permissions' table and info on many-to-many relationships
[1] http://flask-sqlalchemy.pocoo.org/2.3/models/#many-to-many-relationships
"""
from finalwhistle import db


class UserGroup(db.Model):
    """
    Renamed 'SecurityGroup" on logical design diagram - expand system to be more generic and include states
    such as blocked/restricted
    """
    __tablename__ = 'usergroups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False)
    permissions = db.relationship('Permission', secondary=permissions,
                                  backref=db.backref('usergroups', lazy=True))


class Function(db.Model):
    """
    Renamed 'Capability" on logical design diagram - function seems more understandable in the context of
    limiting access to code functions/methods
    """
    __tablename__ = 'functions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)
    description = db.Column(db.String(255), nullable=True)


permissions = db.Table('permissions',
                db.Column('group_id', db.Integer, db.ForeignKey('usergroups.id')),
                db.Column('function_id', db.Integer, db.ForeignKey('functions.id')))
