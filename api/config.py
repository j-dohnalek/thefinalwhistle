from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from football import Base
import os

engine = create_engine('sqlite:///' + os.path.join(os.path.dirname(__file__), 'test.db'))
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
