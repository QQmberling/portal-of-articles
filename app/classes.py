import os
from datetime import datetime

from flask import url_for
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db, TIMEZONE, APP_ROOT
from app.image import get_image_width, get_image_height, save_image


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(TIMEZONE))
    edit_date = db.Column(db.DateTime, default=None)
    able_to_comment = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    author = db.relationship('User', backref=db.backref('articles', lazy=True))

    def __repr__(self):
        return '<Article %r - %r>' % (self.id, self.title)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), unique=True)
    picture_name = db.Column(db.String(20), nullable=False, default='default_male.png')
    date = db.Column(db.DateTime, default=datetime.now(TIMEZONE))
    last_seen = db.Column(db.DateTime, default=datetime.now(TIMEZONE))

    def __repr__(self):
        return '<User %r - %r>' % (self.id, self.username)

    @property
    def password(self):
        raise AttributeError('Пароль - нечитаемый атрибут!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def count_articles(self):
        return len(self.articles)

    def count_comments(self):
        return len(self.comments)

    def url_profile(self):
        return url_for('.profile_with_login', username=self.username)

    def src_other_avatar(self):
        return url_for('static', filename='other_profile_pics/' + self.picture_name)

    def src_main_avatar(self):
        return url_for('static', filename='main_profile_pics/' + self.picture_name)

    def avatar_width_other(self):
        return get_image_width(os.path.join(APP_ROOT, 'static/other_profile_pics', self.picture_name))

    def avatar_height_other(self):
        return get_image_height(os.path.join(APP_ROOT, 'static/other_profile_pics', self.picture_name))

    def avatar_width_main(self):
        return get_image_width(os.path.join(APP_ROOT, 'static/profile_pics', self.picture_name))

    def avatar_height_main(self):
        return get_image_height(os.path.join(APP_ROOT, 'static/profile_pics', self.picture_name))

    def url_main_avatar(self):
        return url_for('static', filename=f'profile_pics/{self.picture_name}')

    def url_other_avatar(self):
        return url_for('static', filename=f'other_profile_pics/{self.picture_name}')

    def save_avatar(self, picture_file):
        return save_image(self.id, picture_file)


class UserInfo(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    about = db.Column(db.String(), nullable=True)
    gender = db.Column(db.String(1), default='М')
    user = db.relationship('User', backref=db.backref('info', lazy=True, uselist=False))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime, default=datetime.now(TIMEZONE))
    edit_date = db.Column(db.DateTime, default=None)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    source = db.relationship('Article', backref=db.backref('comments', lazy=True))
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

    def delete(self):
        return url_for('.comment_delete', id=self.id)

    def edit(self):
        return url_for('.prank', id=self.id)
