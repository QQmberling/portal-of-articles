from flask_login import UserMixin
from flask import url_for
from datetime import datetime
from general import db, TIMEZONE, ROOT_MAIN_PICTURES, ROOT_OTHER_PICTURES
from general.image import get_image_size

# authorship = db.Table('authorship',
#                       db.Column('id', db.Integer, db.ForeignKey('article.id')),
#                       db.Column('id', db.Integer, db.ForeignKey('user.id'))
#                       )


class Article(db.Model):
    #__tablename__ = 'articles'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(TIMEZONE))
    edit_date = db.Column(db.DateTime, default=None)
    able_to_comment = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('articles', lazy=True))
    # author_id = db.Column(db.Integer, db.ForeignKey('User.id'), nullable=False)
    # author = db.relationship('User', backref='article')

    def __repr__(self):
        return '<Article %r - %r>' % (self.id, self.title)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    picture_name = db.Column(db.String(20), nullable=False, default='default_male.png')
    date = db.Column(db.DateTime, default=datetime.now(TIMEZONE))

    def __repr__(self):
        return '<User %r - %r>' % (self.id, self.login)

    def avatar_width_other(self):
        return get_image_size(ROOT_OTHER_PICTURES + self.picture_name)[0]

    def avatar_height_other(self):
        return get_image_size(ROOT_OTHER_PICTURES + self.picture_name)[1]

    def avatar_width_main(self):
        return get_image_size(ROOT_MAIN_PICTURES + self.picture_name)[0]

    def avatar_height_main(self):
        return get_image_size(ROOT_MAIN_PICTURES + self.picture_name)[1]

    def url_main_avatar(self):
        return url_for('static', filename='profile_pics/' + self.picture_name)

    def url_other_avatar(self):
        return url_for('static', filename='other_profile_pics/'+self.picture_name)

    def count_articles(self):
        return len(self.articles)

    def count_comments(self):
        return len(self.comments)


class UserInfo(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    about = db.Column(db.String(), nullable=True)
    gender = db.Column(db.String(1), default='М')
    user = db.relationship('User', uselist=False, backref=db.backref('info', lazy=True))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(TIMEZONE))
    edit_date = db.Column(db.DateTime, default=None)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    source = db.relationship('Article', backref=db.backref('comments', lazy=True))
    author = db.relationship('User', backref=db.backref('comments', lazy=True))
