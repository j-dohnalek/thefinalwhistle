"""
Database models for football system
"""
from sqlalchemy.orm import validates
from sqlalchemy.ext.declarative import declared_attr
from finalwhistle import db


class Person(object):

    # The name and surname will be stored as a single
    # value. The program will never be used to email any referees
    name = db.Column(db.String(100), nullable=False)


class ClubStaff(db.Model, Person):

    __tablename__ = 'clubstaff'

    clubstaff_id = db.Column(db.Integer, primary_key=True)
    role = db.Column(db.String(50), nullable=True)

    @declared_attr
    def team(self):
        return db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)

    # http://docs.sqlalchemy.org/en/rel_0_9/orm/mapped_attributes.html#simple-validators
    @validates('role')
    def validate_role(self, key, value):
        assert value in ['manager']
        return value


class Player(db.Model, Person):

    __tablename__ = 'players'

    player_id = db.Column(db.Integer, primary_key=True)
    shirt_number = db.Column(db.Integer, nullable=True)
    dob = db.Column(db.Date, nullable=True)

    # Update 10-04-2018 new information available to be used in the website
    position = db.Column(db.String(50), nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    # Weight in kilograms
    weight = db.Column(db.Integer, nullable=True)
    # Height in cm
    height = db.Column(db.Integer, nullable=True)

    # Update - 10-04-2018 Removed the storing of information, the data is
    # difficult to obtain in short timescale, possibly future feature
    # injured = db.Column(db.Boolean, nullable=True)
    # suspended = db.Column(db.Boolean, nullable=True)

    transferred_out = db.Column(db.Boolean, nullable=True, default=False)

    @declared_attr
    def current_team(self):
        return db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=True)


class Transfer(db.Model):

    __tablename__ = 'transfers'

    transfer_id = db.Column(db.Integer, primary_key=True)
    transfer_from = db.Column(db.String(50), nullable=False)
    transfer_to = db.Column(db.String(50), nullable=True)
    transfer_window_end = db.Column(db.Date, nullable=False)
    details = db.Column(db.String(50), nullable=False)

    @declared_attr
    def player(self):
        return db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=False)

    @declared_attr
    def season(self):
        return db.Column(db.Integer, db.ForeignKey('seasons.season_id'), nullable=False)


class Referee(db.Model, Person):

    __tablename__ = 'referees'

    referee_id = db.Column(db.Integer, primary_key=True)


class Stadium(db.Model):

    __tablename__ = 'stadiums'

    stadium_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class League(db.Model):

    __tablename__ = 'leagues'

    league_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    api_id = db.Column(db.Integer, nullable=False)


class Season(db.Model):

    __tablename__ = 'seasons'

    season_id = db.Column(db.Integer, primary_key=True)
    end_year = db.Column(db.Date, nullable=False)


class Team(db.Model):

    __tablename__ = 'teams'

    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    name_short = db.Column(db.String(50), nullable=False)

    api_id = db.Column(db.Integer, nullable=False)

    @declared_attr
    def league(self):
        return db.Column(db.Integer, db.ForeignKey('leagues.league_id'), nullable=False)

    @declared_attr
    def stadium(self):
        return db.Column(db.Integer, db.ForeignKey('stadiums.stadium_id'), nullable=False)


class Match(db.Model):

    __tablename__ = 'matches'

    match_id = db.Column(db.Integer, primary_key=True)

    # UPdb.Date 10-04-2018 - Changed from kickoff_time to kickoff, the kickoff
    # stores db.Date and time of the match for the reference
    kickoff = db.Column(db.DateTime, nullable=False)

    @declared_attr
    def home_team(self):
        return db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)

    @declared_attr
    def away_team(self):
        return db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)

    @declared_attr
    def main_referee(self):
        return db.Column(db.Integer, db.ForeignKey('referees.referee_id'), nullable=False)

    @declared_attr
    def season(self):
        return db.Column(db.Integer, db.ForeignKey('seasons.season_id'), nullable=False)


class MatchEvent(object):

    match_event_id = db.Column(db.Integer, primary_key=True)
    minute = db.Column(db.Integer, nullable=False)
    extra_time = db.Column(db.Integer, nullable=True)

    @declared_attr
    def match(self):
        return db.Column(db.Integer, db.ForeignKey('matches.match_id'), nullable=False)


class Goal(db.Model, MatchEvent):

    __tablename__ = 'goals'

    own_goal = db.Column(db.Boolean, nullable=False)
    penalty = db.Column(db.Boolean, nullable=False)

    @declared_attr
    def player(self):
        return db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=False)

    # Not every goal has a assistant (i.e. penalty, own goal)
    @declared_attr
    def assist_player(self):
        return db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=True)


class Substitution(db.Model, MatchEvent):

    __tablename__ = 'substitutions'

    # Not every substitution has a player, if team has more than 3 substitutions
    # and a player is injure he can be only let out
    @declared_attr
    def player_in(self):
        return db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=True)

    @declared_attr
    def player_out(self):
        return db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=False)


class Card(db.Model, MatchEvent):

    __tablename__ = 'cards'

    yellow = db.Column(db.Boolean, nullable=False)

    @declared_attr
    def player(self):
        return db.Column(db.Integer, db.ForeignKey('players.player_id'), nullable=False)


# UPdb.Date 10-04-2018 - Added new pieces of information
class MatchStatistics(db.Model):

    __tablename__ = 'match_statistics'

    stat_id = db.Column(db.Integer, primary_key=True)

    # ft - full time goals
    home_ft_goals = db.Column(db.Integer, nullable=False)
    away_ft_goals = db.Column(db.Integer, nullable=False)
    home_shots = db.Column(db.Integer, nullable=False)
    away_shots = db.Column(db.Integer, nullable=False)
    home_shots_on_target = db.Column(db.Integer, nullable=False)
    away_shots_on_target = db.Column(db.Integer, nullable=False)
    home_corners = db.Column(db.Integer, nullable=False)
    away_corners = db.Column(db.Integer, nullable=False)
    home_fouls = db.Column(db.Integer, nullable=False)
    away_fouls = db.Column(db.Integer, nullable=False)
    home_yellow_cards = db.Column(db.Integer, nullable=False)
    away_yellow_cards = db.Column(db.Integer, nullable=False)
    home_red_cards = db.Column(db.Integer, nullable=False)
    away_red_cards = db.Column(db.Integer, nullable=False)

    @declared_attr
    def match(self):
        return db.Column(db.Integer, db.ForeignKey('matches.match_id'), nullable=False)

    @declared_attr
    def home_team(self):
        return db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)

    @declared_attr
    def away_team(self):
        return db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=False)

    # http://docs.sqlalchemy.org/en/rel_0_9/orm/mapped_attributes.html#simple-validators
    @validates('role')
    def validate_role(self, key, value):
        assert value in [1, 2, 3]
        return value
