import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class Person(object):
    name = Column(String(50), nullable=False)
    surname = Column(String(50), nullable=True)


class Player(Person, Base):

    __tablename__ = 'Player'

    player_id = Column(Integer, primary_key=True)
    dob = Column(Date, nullable=False)
    current_team = Column(Integer, nullable=False)
    injured = Column(Boolean, nullable=False)
    suspended = Column(Boolean, nullable=False)
    shirt_number = Column(Integer, nullable=True)
    position = Column(String(50), nullable=True)


class Team(Base):
    __tablename__ = 'Team'

    team_id = Column(Integer, primary_key=True)
    league = Column(Integer, nullable=False)
    stadium = Column(Integer, nullable=False)
    name = Column(String(50), nullable=False)







# Create an engine that stores data in the local directory's
# sqlalchemy_example.db file.
engine = create_engine('mysql+mysqldb://root:123456@localhost/finalwhistle')

# Create all tables in the engine. This is equivalent to "Create Table"
# statements in raw SQL.
Base.metadata.create_all(engine)
