import base64

import pytest

from app import create_app, db
from app.models import User, Article, Comment


@pytest.fixture(scope='session', autouse=True)
def app():
    app = create_app('testing')
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    yield app
    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_request(app):
    with app.test_request_context() as request:
        yield request


@pytest.fixture
def logged_john(client):
    response = client.post('/login', data={'username': 'john', 'password': 'catt'}, follow_redirects=True)
    yield client


@pytest.fixture
def logged_mike(client):
    response = client.post('/login', data={'username': 'mike', 'password': 'dogg'}, follow_redirects=True)
    yield client


@pytest.fixture
def st_user():
    u = User.create({'username': 'st_user', 'password': 'password', 'email': 'st_user@gmail.com'})
    yield u
    User.query.delete()
    # print(len(UserInfo.query.all()), len(User.query.all()))


@pytest.fixture
def st_article(st_user):
    article = Article.create({'title': 'st_article', 'intro': 'st_intro', 'text': 'st_text', 'author_id': st_user.id})
    yield article
    Article.query.delete()


@pytest.fixture
def st_comment(st_user, st_article):
    comment = Comment.create({'text': 'st_comment', 'article_id': st_article.id, 'author_id': st_user.id})
    yield comment
    Comment.query.delete()


@pytest.fixture
def st_token(st_user, client):
    valid_credentials = base64.b64encode(b'st_user:password').decode("utf-8")
    response = client.get('/api/v1/users/get_token/', headers={"Authorization": "Basic " + valid_credentials})
    yield response.json['token']


@pytest.fixture
def st_user2():
    u = User.create({'username': 'st_user2', 'password': 'password', 'email': 'st_user2@gmail.com'})
    yield u
    User.query.delete()


@pytest.fixture
def st_token2(st_user2, client):
    valid_credentials = base64.b64encode(b'st_user2:password').decode("utf-8")
    response = client.get('/api/v1/users/get_token/', headers={"Authorization": "Basic " + valid_credentials})
    yield response.json['token']
