"""
Small miscellaneous functions which may be of use in various places
"""


def new_uuid():
    import uuid
    return str(uuid.uuid4())
