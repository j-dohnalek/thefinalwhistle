"""
Database models for permissions and security groups system

See [1] for explanation of 'permissions' table and info on many-to-many relationships

[1] http://flask-sqlalchemy.pocoo.org/2.3/models/#many-to-many-relationships
"""
from finalwhistle import db


class SecurityGroup(db.Model):
    __tablename__ = 'sec_groups'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(30), nullable=False)
    permissions = db.relationship('Permission', secondary=permissions,
                                  backref=db.backref('sec_groups', lazy=True))


class Function(db.Model):
    """
    Renamed 'Capability" on ER diagram - function seems more understandable in the context of limiting access
    to code functions/methods
    """
    __tablename__ = 'functions'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(30), nullable=False)


permissions = db.Table('permissions',
                db.Column('group_id', db.Integer, db.ForeignKey('sec_groups.id')),
                db.Column('function_id', db.Integer, db.ForeignKey('permissions.id')))