

def get_or_create(session, model, **kwargs):
    """
    Get an object from the database if it already
    exists or create it if it does not.

    See https://stackoverflow.com/questions/2546207
    :param session: SQLAlchemy session
    :param model: SQLAlchemy model object
    :param kwargs: table attributes
    :return:
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance


def record_exists(session, model, **kwargs):
    """
    Get an object from the database if it already
    exists or create it if it does not.

    See https://stackoverflow.com/questions/2546207
    :param session: SQLAlchemy session
    :param model: SQLAlchemy model object
    :param kwargs: table attributes
    :return:
    """
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return True
    else:
        return False
