import datetime
import io
import os

import jwt
from flask import url_for, current_app
from flask_login import UserMixin
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.datastructures import FileStorage

from app import db
from app.image import save_image


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime(), default=func.now())
    edit_date = db.Column(db.DateTime(), default=None)
    able_to_comment = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    author = db.relationship('User', backref=db.backref('articles', lazy=True, cascade="all,delete,delete-orphan"))

    def __repr__(self):
        return '<Article %r - %r>' % (self.id, self.title)

    @staticmethod
    def create(json):
        if 'able_to_comment' in json:
            json['able_to_comment'] = int(json['able_to_comment'])
        article = Article(**json)
        db.session.add(article)
        db.session.commit()
        return article

    def upd(self, json):
        json['edit_date'] = func.now()
        Article.query.filter(Article.id == self.id).update(json)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def new(self):
        db.session.add(self)
        db.session.commit()
        return self

    @property
    def url(self):
        return url_for('api.articles_single_article', id=self.id, _external=True)

    @property
    def author_url(self):
        return url_for('api.users_single_user', id=self.author_id, _external=True)

    @property
    def delete_url(self):
        return url_for('main.article_delete', id=self.id)

    @property
    def update_url(self):
        return url_for('main.article_update', id=self.id)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(64), unique=True)

    def __repr__(self):
        return '<User %r - %r>' % (self.id, self.username)

    @staticmethod
    def create(json):
        json['email'] = json['email'].lower()
        user = User(**json)
        userinfo = UserInfo()
        db.session.add(user)
        db.session.add(userinfo)
        db.session.commit()
        return user

    def upd(self, json):
        if 'avatar' in json and json['avatar'] is not None:
            self.update_avatar(json.pop('avatar'))
        UserInfo.query.filter(UserInfo.id == self.id).update(json)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def new(self):
        db.session.add(self)
        db.session.commit()
        userinfo = UserInfo()
        db.session.add(userinfo)
        db.session.commit()
        return self

    @property
    def url(self):
        return url_for('api.users_single_user', id=self.id, _external=True)

    @property
    def password(self):
        raise AttributeError('Пароль - нечитаемый атрибут!')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def count_articles(self):
        return len(self.articles)

    @property
    def count_comments(self):
        return len(self.comments)

    @property
    def url_profile(self):
        return url_for('main.profile_with_login', username=self.username)

    @property
    def url_avatar(self):
        """ Статические файлы на хостинге хероку постоянно удаляются, поэтому
            картинка будет воспроизводиться из бд, если статическая такая не нашлась.
         """
        if not os.path.isfile(os.path.join(current_app.root_path,
                                           url_for('static', filename=f'profile_pics/{self.info.picture_name}')[1:])):
            """ Нет статического файла картинки
            """
            if self.info.picture_file is not None:
                """ Есть какое-то бинарное значение в бд => воспроизводим его в статический файл
                """
                self.update_avatar(FileStorage(io.BytesIO(self.info.picture_file), self.info.picture_name, name='file', content_type='image/png'))
            else:
                """ Нет ничего в бд => используем стандартные статические файлы
                """
                self.info.picture_name = ('М' == self.info.gender) * 'defaults/default_male.png' + \
                                         ('М' != self.info.gender) * 'defaults/default_female.png'
        return url_for('static', filename=f'profile_pics/{self.info.picture_name}')

    def update_avatar(self, picture_file):
        picture_name, picture_file = save_image(self.id, picture_file, self.info.picture_name)
        picture_file.stream.seek(0) # Так как уже вызывался .read() в image.py , то нужно отмотать в начало бинарник
        self.info.picture_file = picture_file.read()
        self.info.picture_name = picture_name
        db.session.commit()

    @staticmethod
    def get_authors():
        # full_query = db.session.query(User.username, func.count(Article.id)).group_by(Article.author_id).join(User, Article.author_id == User.id).order_by(func.count(Article.id).desc()).all()
        subquery = db.session.query(Article.author_id, func.count(Article.id).label('count')).group_by(
            Article.author_id).subquery()
        authors = User.query.join(subquery, subquery.c.author_id == User.id).order_by(subquery.c.count.desc()).all()
        return authors

    def generate_auth_token(self, expiration=3600):
        token = jwt.encode({"id": self.id, 'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(
            seconds=expiration)},
                           current_app.config['SECRET_KEY'],
                           algorithm="HS256")
        return token

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return None
        return User.query.get(data['id'])

    def ping(self):
        self.info.last_seen = func.now()
        db.session.commit()


class UserInfo(db.Model):
    id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(30), nullable=True)
    last_name = db.Column(db.String(30), nullable=True)
    about = db.Column(db.String(), nullable=True)
    gender = db.Column(db.String(1))
    picture_name = db.Column(db.String(200), nullable=False, default='defaults/default_male.png')
    picture_file = db.Column(db.LargeBinary, nullable=True, default=None)
    date = db.Column(db.DateTime, default=func.now())
    last_seen = db.Column(db.DateTime, default=func.now())
    user = db.relationship('User', backref=db.backref('info', uselist=False, cascade="all,delete,delete-orphan"))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text(), nullable=False)
    date = db.Column(db.DateTime, default=func.now())
    edit_date = db.Column(db.DateTime, default=None)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id', ondelete="CASCADE"))
    author_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    article = db.relationship('Article', backref=db.backref('comments', lazy=True, cascade="all,delete,delete-orphan"))
    author = db.relationship('User', backref=db.backref('comments', lazy=True, cascade="all,delete,delete-orphan"))

    @staticmethod
    def create(json):
        comment = Comment(**json)
        db.session.add(comment)
        db.session.commit()
        return comment

    def upd(self, json):
        json['edit_date'] = func.now()
        Comment.query.filter(Comment.id == self.id).update(json)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def new(self):
        db.session.add(self)
        db.session.commit()
        return self

    @property
    def url(self):
        return url_for('api.comments_single_comment', id=self.id, _external=True)

    @property
    def article_url(self):
        return url_for('api.articles_single_article', id=self.article_id, _external=True)

    @property
    def author_url(self):
        return url_for('api.users_single_user', id=self.author_id, _external=True)

    @property
    def delete_url(self):
        return url_for('main.comment_delete', id=self.id)

    @property
    def update_url(self):
        return url_for('main.prank', id=self.id)
