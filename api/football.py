from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import validates
from sqlalchemy import Column, Date, Integer, String, Boolean, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class Person(object):

    # The name and surname will be stored as a single
    # value. The program will never be used to email any referees
    name = Column(String(100), nullable=False)


class ClubStaff(Base, Person):

    __tablename__ = 'clubstaff'

    clubstaff_id = Column(Integer, primary_key=True)
    role = Column(String(50), nullable=True)

    @declared_attr
    def team(self):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)

    # http://docs.sqlalchemy.org/en/rel_0_9/orm/mapped_attributes.html#simple-validators
    @validates('role')
    def validate_role(self, key, value):
        assert value in ['manager']
        return value


class Player(Base, Person):

    __tablename__ = 'player'

    player_id = Column(Integer, primary_key=True)
    shirt_number = Column(Integer, nullable=True)
    dob = Column(Date, nullable=True)

    # UPDATE 10-04-2018 new information available to be used in the website
    position = Column(String(50), nullable=True)
    nationality = Column(String(50), nullable=True)
    # Weight in kilograms
    weight = Column(Integer, nullable=True)
    # Height in cm
    height = Column(Integer, nullable=True)

    # UPDATE - 10-04-2018 Removed the storing of information, the data is
    # difficult to obtain in short timescale, possibly future feature
    # injured = Column(Boolean, nullable=True)
    # suspended = Column(Boolean, nullable=True)

    transferred_out = Column(Boolean, nullable=True, default=False)

    @declared_attr
    def current_team(self):
        return Column(Integer, ForeignKey('team.team_id'), nullable=True)


class Transfer(Base):

    __tablename__ = 'transfer'

    transfer_id = Column(Integer, primary_key=True)
    transfer_from = Column(String(50), nullable=False)
    transfer_to = Column(String(50), nullable=True)
    transfer_window_end = Column(Date, nullable=False)
    details = Column(String(50), nullable=False)

    @declared_attr
    def player(self):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)

    @declared_attr
    def season(self):
        return Column(Integer, ForeignKey('season.season_id'), nullable=False)


class Referee(Base, Person):

    __tablename__ = 'referee'

    referee_id = Column(Integer, primary_key=True)


class Stadium(Base):

    __tablename__ = 'stadium'

    stadium_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)


class League(Base):

    __tablename__ = 'league'

    league_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    api_id = Column(Integer, nullable=False)


class Season(Base):

    __tablename__ = 'season'

    season_id = Column(Integer, primary_key=True)
    end_year = Column(Date, nullable=False)


class Team(Base):

    __tablename__ = 'team'

    team_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    name_short = Column(String(50), nullable=False)

    api_id = Column(Integer, nullable=False)

    @declared_attr
    def league(self):
        return Column(Integer, ForeignKey('league.league_id'), nullable=False)

    @declared_attr
    def stadium(self):
        return Column(Integer, ForeignKey('stadium.stadium_id'), nullable=False)


class Match(Base):

    __tablename__ = 'match'

    match_id = Column(Integer, primary_key=True)

    # UPDATE 10-04-2018 - Changed from kickoff_time to kickoff, the kickoff
    # stores date and time of the match for the reference
    kickoff = Column(DateTime, nullable=False)

    @declared_attr
    def home_team(self):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)

    @declared_attr
    def away_team(self):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)

    @declared_attr
    def main_referee(self):
        return Column(Integer, ForeignKey('referee.referee_id'), nullable=False)

    @declared_attr
    def season(self):
        return Column(Integer, ForeignKey('season.season_id'), nullable=False)


class MatchEvent(object):

    match_event_id = Column(Integer, primary_key=True)
    minute = Column(Integer, nullable=False)
    extra_time = Column(Integer, nullable=True)

    @declared_attr
    def match(self):
        return Column(Integer, ForeignKey('match.match_id'), nullable=False)


class Goal(Base, MatchEvent):

    __tablename__ = 'goal'

    own_goal = Column(Boolean, nullable=False)
    penalty = Column(Boolean, nullable=False)

    @declared_attr
    def player(self):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)

    # Not every goal has a assistant (i.e. penalty, own goal)
    @declared_attr
    def assist_player(self):
        return Column(Integer, ForeignKey('player.player_id'), nullable=True)


class Substitution(Base, MatchEvent):

    __tablename__ = 'substitution'

    # Not every substitution has a player, if team has more than 3 substitutions
    # and a player is injure he can be only let out
    @declared_attr
    def player_in(self):
        return Column(Integer, ForeignKey('player.player_id'), nullable=True)

    @declared_attr
    def player_out(self):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)


class Card(Base, MatchEvent):

    __tablename__ = 'card'

    yellow = Column(Boolean, nullable=False)

    @declared_attr
    def player(self):
        return Column(Integer, ForeignKey('player.player_id'), nullable=False)


# UPDATE 10-04-2018 - Added new pieces of information
class MatchStatistics(Base):

    __tablename__ = 'match_statistics'

    stat_id = Column(Integer, primary_key=True)

    # ft - full time goals
    home_ft_goals = Column(Integer, nullable=False)
    away_ft_goals = Column(Integer, nullable=False)

    # ht - half time goals
    home_ht_goals = Column(Integer, nullable=False)
    away_ht_goals = Column(Integer, nullable=False)

    # 1 - home team win
    # 2 - away team win
    # 3 - draw
    ft_result = Column(Integer, nullable=False)
    ht_result = Column(Integer, nullable=False)

    home_shots = Column(Integer, nullable=False)
    away_shots = Column(Integer, nullable=False)
    home_shots_on_target = Column(Integer, nullable=False)
    away_shots_on_target = Column(Integer, nullable=False)
    home_corners = Column(Integer, nullable=False)
    away_corners = Column(Integer, nullable=False)
    home_fouls = Column(Integer, nullable=False)
    away_fouls = Column(Integer, nullable=False)
    home_yellow_cards = Column(Integer, nullable=False)
    away_yellow_cards = Column(Integer, nullable=False)
    home_red_cards = Column(Integer, nullable=False)
    away_red_cards = Column(Integer, nullable=False)

    @declared_attr
    def match(self):
        return Column(Integer, ForeignKey('match.match_id'), nullable=False)

    @declared_attr
    def home_team(self):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)

    @declared_attr
    def away_team(self):
        return Column(Integer, ForeignKey('team.team_id'), nullable=False)

    # http://docs.sqlalchemy.org/en/rel_0_9/orm/mapped_attributes.html#simple-validators
    @validates('role')
    def validate_role(self, key, value):
        assert value in [1, 2, 3]
        return value
