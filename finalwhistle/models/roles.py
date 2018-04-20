"""
Define usergroups and permissions
"""
from flask_permissions.models import Role
from finalwhistle import db

admin = Role('admin')
editor = Role('editor')
user = Role('user')
restricted = Role('restricted_user')


def init_roles_db():
    db.session.add(admin)
    db.session.add(editor)
    db.session.add(user)
    db.session.add(restricted)
    db.session.commit()




