"""
Database model for contact page message
"""
from finalwhistle import db
from sqlalchemy import func


class Message(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_name = db.Column(db.String(100), nullable=True)
    sender_email = db.Column(db.String(255), nullable=True)
    subject = db.Column(db.String(50), nullable=True)
    body = db.Column(db.Text, nullable=True)

    posted_at = db.Column(db.DateTime, server_default=func.now())
