from datetime import datetime

from flask import url_for, current_app
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import func
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app.exceptions import ValidationError
from app import db, TIMEZONE
from app.image import save_image


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

    def to_json(self):
        json_article = {
            'id': self.id,
            'url': url_for('api.get_article', id=self.id),
            'title': self.title,
            'intro': self.intro,
            'text': self.text,
            'date': self.date,
            'edit_date': self.edit_date,
            'able_to_comment': self.able_to_comment,
            'author_id': self.author_id,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments': [comment.to_json()['url'] for comment in self.comments],
        }
        return json_article

    @staticmethod
    def from_json(json_article, author_id):
        title = json_article.get('title')
        intro = json_article.get('intro')
        text = json_article.get('text')
        if title is None or title == '' or intro is None or intro == '' or text is None or text == '':
            raise ValidationError('title, intro, text must be filled')
        return Article(title=title, intro=intro, text=text, author_id=author_id)

    @staticmethod
    def get_articles():
        articles = Article.query.all()
        return articles

    @staticmethod
    def api_fields():
        return 'title', 'intro', 'text', 'able_to_comment'


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

    def url_avatar(self):
        return url_for('static', filename=f'profile_pics/{self.picture_name}')

    def save_avatar(self, picture_file):
        return save_image(self.id, picture_file)

    def to_json(self):
        json_user = {
            'id': self.id,
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'email': self.email,
            'first_name': self.info.first_name,
            'last_name': self.info.last_name,
            'gender': self.info.gender,
            'about': self.info.about,
            'register_date': self.date,
            'last_seen': self.last_seen,
            'count_articles': self.count_articles(),
            'articles': [article.to_json()['url'] for article in self.articles],
            'count_comments': self.count_comments(),
            'comments': [comment.to_json()['url'] for comment in self.comments],
        }
        return json_user

    # def edit(self, json):
    #     try:
    #         self.q
    #     if title is None or title == '' or intro is None or intro == '' or text is None or text == '':
    #         raise ValidationError('title, intro, text must be filled')
    #     return Article(title=title, intro=intro, text=text)

    # def update(self, updates):
    #     for i in updates.

    @staticmethod
    def get_authors():
        # full_query = db.session.query(User.username, func.count(Article.id)).group_by(Article.author_id).join(User, Article.author_id == User.id).order_by(func.count(Article.id).desc()).all()
        subquery = db.session.query(Article.author_id, func.count(Article.id).label('count')).group_by(Article.author_id).subquery()
        authors = User.query.join(subquery, subquery.c.author_id == User.id).order_by(subquery.c.count.desc()).all()
        return authors

    @staticmethod
    def get_users():
        users = User.query.all()
        return users

    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    @staticmethod
    def api_fields():
        return 'first_name', 'last_name', 'gender', 'about'


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

    def to_json(self):
        json_comment = {
            'id': self.id,
            'url': url_for('api.get_comment', id=self.id),
            'text': self.text,
            'date': self.date,
            'edit_date': self.edit_date,
            'article_id': self.article_id,
            'article_url': url_for('api.get_article', id=self.article_id),
            'author_id': self.author_id,
            'author_url': url_for('api.get_user', id=self.author_id),
        }
        return json_comment

    @staticmethod
    def from_json(json_comment, article_id, author_id):
        text = json_comment.get('text')
        if text is None or text == '':
            raise ValidationError('text must be filled')
        return Comment(text=text, article_id=article_id, author_id=author_id)

    @staticmethod
    def get_comments():
        comments = Comment.query.all()
        return comments
