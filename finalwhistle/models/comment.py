"""
Database models for comment system
"""
from sqlalchemy import func

from finalwhistle import db


class Comment(object):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    posted_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    posted_at = db.Column(db.DateTime, server_default=func.now())
    edited_at = db.Column(db.DateTime, server_onupdate=func.now())


class ArticleComment(db.Model, Comment):
    __tablename__ = 'article_comments'
    article_id = db.Column(db.Integer, db.ForeignKey('articles.id'), nullable=False)


class MatchComment(db.Model, Comment):
    __tablename__ = 'match_comments'
    article_id = db.Column(db.Integer, db.ForeignKey('matches.id'), nullable=False)


