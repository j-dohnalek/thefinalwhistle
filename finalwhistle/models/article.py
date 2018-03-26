"""
Database models for news article system
"""
from finalwhistle import db
from sqlalchemy.orm import validates


class Article(db.Model):
    __tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False)
    last_edited = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String, nullable=False)

    # http://docs.sqlalchemy.org/en/rel_0_9/orm/mapped_attributes.html#simple-validators
    @validates('status')
    def validate_status(self, key, value):
        assert value in ['Published', 'Draft', 'Hidden']
        return value


class ArticleComment(db.Model):
    __tablename__ = 'article_comments'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    author = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    on_article = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)
    content = db.Column(db.String, nullable=False)
    submitted_at = db.Column(db.DateTime, nullable=False)
    last_edited = db.Column(db.DateTime, nullable=False)


class ArticleCategory(db.Model):
    __tablename__ = 'article_categories'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
