from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean


Base = declarative_base()


class Person(object):

    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=True)


class ClubStaff(Base, Person):

    __tablename__ = 'clubstaff'

    clubstaff_id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=True)

    @declared_attr
    def team(cls):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)  # (FK)


class Player(Base, Person):

    __tablename__ = 'player'

    player_id = Column(Integer, primary_key=True)
    dob = Column(Date, nullable=False)
    injured = Column(Boolean, nullable=False)
    suspended = Column(Boolean, nullable=False)
    shirt_number = Column(Integer, nullable=True)
    position = Column(String(50), nullable=True)

    @declared_attr
    def current_team(cls):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)  # (FK)


class Referee(Base, Person):

    __tablename__ = 'referee'

    referee_id = Column(Integer, primary_key=True)


class Stadium(Base):

    __tablename__ = 'stadium'

    stadium_id = Column(Integer, primary_key=True)  # (PK)
    name = Column(String(50), nullable=False)


class League(Base):

    __tablename__ = 'league'

    league_id = Column(Integer, primary_key=True)  # (PK)
    name = Column(String(50), nullable=False)


class Season(Base):

    __tablename__ = 'season'

    season_id = Column(Integer, primary_key=True)  # (PK)
    end_year = Column(Date, nullable=False)


class Team(Base):

    __tablename__ = 'team'

    team_id = Column(Integer, primary_key=True)  # (PK)
    name = Column(String(50), nullable=False)

    @declared_attr
    def league(cls):
        return Column(Integer, ForeignKey('league.league_id'), nullable=False)  # (FK)

    @declared_attr
    def stadium(cls):
        return Column(Integer, ForeignKey('stadium.stadium_id'), nullable=False)  # (FK)


class Transfer(Base):

    __tablename__ = 'transfer'

    transfer_id = Column(Integer, primary_key=True)  # (PK)
    transfer_from = Column(String(50), nullable=False)
    transfer_to = Column(String(50), nullable=False)

    @declared_attr
    def season(cls):
        return Column(Integer, ForeignKey('season.season_id'), nullable=False)  # (FK)

    @declared_attr
    def player(cls):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)  # (FK)

    @declared_attr
    def club_staff(cls):
        return Column(Integer, ForeignKey('clubstaff.clubstaff_id'), nullable=False)  # (FK)


class Match(Base):

    __tablename__ = 'match'

    match_id = Column(Integer, primary_key=True)  # (PK)
    kickoff_time = Column(Date, nullable=False)

    @declared_attr
    def home_team(cls):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)  # (FK)

    @declared_attr
    def away_team(cls):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)  # (FK)

    @declared_attr
    def main_referee(cls):
        return Column(Integer, ForeignKey('referee.referee_id'), nullable=False)  # (FK)

    @declared_attr
    def season(cls):
        return Column(Integer, ForeignKey('season.season_id'), nullable=False)  # (FK)


class MatchEvent(object):

    match_event_id = Column(Integer, primary_key=True)
    match_minute = Column(Integer, nullable=False)
    extra_time = Column(Integer, nullable=True)

    @declared_attr
    def match(cls):
        return Column(Integer, ForeignKey('match.match_id'), nullable=False)  # (FK)


class Goal(Base, MatchEvent):

    __tablename__ = 'goal'

    own_goal = Column(Boolean, nullable=False)
    penalty = Column(Boolean, nullable=False)

    @declared_attr
    def player(cls):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)  # (FK)

    @declared_attr
    def assist_player(cls):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)  # (FK)


class Substitution(Base, MatchEvent):

    __tablename__ = 'substitution'

    @declared_attr
    def player_in(cls):
        return Column(Integer, ForeignKey('player.player_id'), nullable=True)  # (FK)

    @declared_attr
    def player_out(cls):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)  # (FK)


class Card(Base, MatchEvent):

    __tablename__ = 'card'

    @declared_attr
    def player(cls):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)  # (FK)

    yellow = Column(Boolean, nullable=False)


# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('mysql+mysqldb://root:123456@localhost/test')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
