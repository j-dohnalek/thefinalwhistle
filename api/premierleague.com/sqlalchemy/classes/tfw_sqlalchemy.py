

class MatchEvent(Object):

    """Class MatchEvent"""
    __tablename__ = 'MatchEvent'

    # Attributes:

    match_event_id = Column(Integer, primary_key=True)
    match = Column(Integer, nullable=False) # (FK)
    match_minute = Column(Integer, nullable=False)
    extra_time = Column(Integer, nullable=False)

    # Operations


class Goal(Base, MatchEvent):

    """Class Goal"""
    __tablename__ = 'Goal'

    # Attributes:

    player = Column(Integer, nullable=False) # (FK)
    assist_player = Column(Integer, nullable=False) # (FK)
    own_goal = Column(Boolean, nullable=False)
    penalty = Column(Boolean, nullable=False)

    # Operations


class Substitution(Base, MatchEvent):

    """Class Substitution"""
    __tablename__ = 'Substitution'

    # Attributes:

    player_in = Column(Integer, nullable=False) # (FK)
    player_out = Column(Integer, nullable=False) # (FK)

    # Operations




class Card(Base, MatchEvent):

    """ Class Card """
    __tablename__ = 'Card'

    # Attributes:

    player = Column(Integer, nullable=False) # (FK)
    yellow = Column(Boolean, nullable=False)

    # Operations
