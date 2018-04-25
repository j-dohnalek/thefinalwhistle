"""
Database models for news article system
"""
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from finalwhistle import db
from sqlalchemy.orm import validates


def create_new_article(author_id, title, body):
    try:
        new_article = Article(author_id=author_id,
                              title=title,
                              body=body)
        db.session.add(new_article)
        db.session.commit()
        return new_article
    except SQLAlchemyError:
        print('something went wrong when making a new account!')
    return None


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.String, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    # last_edited = db.Column(db.DateTime, nullable=False)
    # status = db.Column(db.String, nullable=False)

    def __init__(self, author_id, title, body):
        self.author_id = author_id
        self.body = body
        self.title = title

    def preview(self, limit=60):
        """
        Returns characters up to 'length' after removing html tags from article body
        :param limit: preview length
        :return: article preview 'length' characters long
        """
        from helpers import remove_html_tags
        stripped = remove_html_tags(self.body)
        return stripped[:limit]


    # http://docs.sqlalchemy.org/en/rel_0_9/orm/mapped_attributes.html#simple-validators
    # @validates('status')
    # def validate_status(self, key, value):
    #     assert value in ['Published', 'Hidden']
    #     return value