"""
Database models for news article system
"""
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from finalwhistle import db

from sqlalchemy.ext.declarative import declared_attr

from finalwhistle.models.user import User
from finalwhistle.models.comment import ArticleComment


def create_new_article(author_id, title, body):
    try:
        new_article = Article(author_id=author_id,
                              title=title,
                              body=body,
                              featured_image='images/featured/default.jpg')
        db.session.add(new_article)
        db.session.commit()
        return new_article
    except SQLAlchemyError:
        print('something went wrong when making a new account!')
    return None


def update_existing_article(id, title, body):
    try:
        article = Article.query.filter_by(id=id).first()
        article.title = title
        article.body = body
        db.session.commit()
        return article
    except SQLAlchemyError:
        print('something went wrong when making a new account!')
    return None


def get_latest_news(count=5):
    news = Article.query \
        .join(User, User.id == Article.author_id) \
        .outerjoin(ArticleComment, ArticleComment.article_id == Article.id) \
        .add_columns(User.real_name,
                     Article.id,
                     Article.body,
                     Article.submitted_at,
                     Article.title,
                     Article.featured_image,
                     func.count(ArticleComment.id).label('comments')) \
        .group_by(Article.id).order_by(Article.submitted_at.desc()).limit(count).all()
    return news


class Article(db.Model):

    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User')
    # TODO: map author_name attribute
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.String, nullable=False)
    featured_image = db.Column(db.String, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False, server_default=func.now())
    # last_edited = db.Column(db.DateTime, nullable=False)
    # status = db.Column(db.String, nullable=False)

    @declared_attr
    def author_id(self):
        return db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)


    def __init__(self, author_id, title, body):
        self.author_id = author_id
        self.body = body
        self.title = title

    # http://docs.sqlalchemy.org/en/rel_0_9/orm/mapped_attributes.html#simple-validators
    # @validates('status')
    # def validate_status(self, key, value):
    #     assert value in ['Published', 'Hidden']
    #     return value