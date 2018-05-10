"""
Database model for contact page message
"""
from finalwhistle import db
from sqlalchemy import func, asc


def fetch_all_messages():
    """
    Fetch all messages sent through the contact form
    :return:
    """
    return Message.query.order_by(asc(Message.id)).all()


def delete_message(id):
    """
    Delete message
    :param id: id of message to delete
    :return: list of messages
    """
    message = Message.query.filter(Message.id == id).first()
    if message is not None:
        Message.query.filter(Message.id == id).delete()
        db.session.commit()
    return fetch_all_messages()


class Message(db.Model):

    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sender_name = db.Column(db.String(100), nullable=True)
    sender_email = db.Column(db.String(255), nullable=True)
    subject = db.Column(db.String(50), nullable=True)
    body = db.Column(db.Text, nullable=True)

    posted_at = db.Column(db.DateTime, server_default=func.now())
