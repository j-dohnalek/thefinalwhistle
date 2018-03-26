"""
Small miscellaneous functions which may be of use in various places
"""
from finalwhistle.models.user import User


def new_uuid():
    import uuid
    return str(uuid.uuid4())
