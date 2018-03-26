"""
Database models for comment system
"""
from finalwhistle import db

class Comment(db.Model):
    __tablename__ = 'comments'