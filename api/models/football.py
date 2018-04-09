from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declared_attr


db = SQLAlchemy()


class Person(object):

    name = db.Column(db.String(255), nullable=False)


class ClubStaff(db.Model, Person):

    __tablename__ = 'clubstaff'

    clubstaff_id = db.Column(db.Integer, primary_key=True)
    # Missed in Logical Model
    role = db.Column(db.String(50), nullable=True)

    @declared_attr
    def team(cls):
        return db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)


class Player(db.Model, Person):

    __tablename__ = 'player'

    player_id = db.Column(db.Integer, primary_key=True)
    dob = db.Column(db.Date, nullable=False)
    shirt_number = db.Column(db.Integer, nullable=True)
    nationality = db.Column(db.String(50), nullable=True)
    position = db.Column(db.String(50), nullable=True)
    weight = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)

    @declared_attr
    def current_team(cls):
        return db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)


class Referee(db.Model, Person):

    __tablename__ = 'referee'

    referee_id = db.Column(db.Integer, primary_key=True)


class Stadium(db.Model):

    __tablename__ = 'stadium'

    stadium_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class League(db.Model):

    __tablename__ = 'league'

    league_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class Season(db.Model):

    __tablename__ = 'season'

    season_id = db.Column(db.Integer, primary_key=True)
    end_year = db.Column(db.Date, nullable=False)


class Team(db.Model):

    __tablename__ = 'team'

    team_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    @declared_attr
    def league(cls):
        return db.Column(db.Integer, db.ForeignKey('league.league_id'), nullable=False)

    @declared_attr
    def stadium(cls):
        return db.Column(db.Integer, db.ForeignKey('stadium.stadium_id'), nullable=False)


class Transfer(db.Model):

    __tablename__ = 'transfer'

    transfer_id = db.Column(db.Integer, primary_key=True)
    transfer_from = db.Column(db.String(50), nullable=False)
    transfer_to = db.Column(db.String(50), nullable=False)

    @declared_attr
    def season(cls):
        return db.Column(db.Integer, db.ForeignKey('season.season_id'), nullable=False)

    @declared_attr
    def player(cls):
        return db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=False)

    @declared_attr
    def club_staff(cls):
        return db.Column(db.Integer, db.ForeignKey('clubstaff.clubstaff_id'), nullable=False)


class Match(db.Model):

    __tablename__ = 'match'

    match_id = db.Column(db.Integer, primary_key=True)
    kickoff_time = db.Column(db.Date, nullable=False)

    @declared_attr
    def home_team(cls):
        return db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)

    @declared_attr
    def away_team(cls):
        return db.Column(db.Integer, db.ForeignKey('team.team_id'), nullable=False)

    @declared_attr
    def main_referee(cls):
        return db.Column(db.Integer, db.ForeignKey('referee.referee_id'), nullable=False)

    @declared_attr
    def season(cls):
        return db.Column(db.Integer, db.ForeignKey('season.season_id'), nullable=False)


class MatchEvent(object):

    match_event_id = db.Column(db.Integer, primary_key=True)
    minute = db.Column(db.Integer, nullable=False)
    extra_time = db.Column(db.Integer, nullable=True)

    @declared_attr
    def match(cls):
        return db.Column(db.Integer, db.ForeignKey('match.match_id'), nullable=False)


class Goal(db.Model, MatchEvent):

    __tablename__ = 'goal'

    own_goal = db.Column(db.Boolean, nullable=False)
    penalty = db.Column(db.Boolean, nullable=False)

    @declared_attr
    def player(cls):
        return db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=False)

    @declared_attr
    def assist_player(cls):
        return db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=False)


class Substitution(db.Model, MatchEvent):

    __tablename__ = 'substitution'

    @declared_attr
    def player_in(cls):
        return db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=True)

    @declared_attr
    def player_out(cls):
        return db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=False)


class Card(db.Model, MatchEvent):

    __tablename__ = 'card'

    yellow = db.Column(db.Boolean, nullable=False)

    @declared_attr
    def player(cls):
        return db.Column(db.Integer, db.ForeignKey('player.player_id'), nullable=False)
