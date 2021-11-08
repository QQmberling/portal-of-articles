import base64

from app import db
from app.models import User, Article, Comment


def test_users_get(client, st_user):
    response = client.get('/api/v1/users/')
    assert response.status_code == 200
    data = response.json['users']
    users = User.query.all()
    for i, user in enumerate(users):
        assert data[i]['username'] == users[i].username
        assert data[i]['first_name'] == users[i].info.first_name
        assert data[i]['url'] == users[i].url


def test_users_post(client, st_user):
    response = client.post('/api/v1/users/',
                           json={'username': 'api_user', 'password': 'password', 'email': 'api@gmail.com'})
    assert response.status_code == 200
    user = db.session.query(User).filter_by(username='api_user').first()
    assert user is not None


def test_users_post_with_incorrect_input(client, st_user):
    response = client.post('/api/v1/users/', json={'username': 'api_user', 'email': 'api@gmail.com'})
    assert response.status_code == 400
    user = db.session.query(User).filter_by(username='api_user').first()
    assert user is None

    response = client.post('/api/v1/users/', json={})
    assert response.status_code == 400

    response = client.post('/api/v1/users/', json={'username': '', 'password': 'password', 'email': 'api@gmail.com'})
    assert response.status_code == 400


def test_users_authors_get(client, st_article):
    User(username='temp', password='password', email='temp@mail.ru').new()
    response = client.get('/api/v1/users/authors/')
    assert response.status_code == 200
    authors = User.get_authors()
    assert len(authors) == len(response.json['users'])


def test_users_gettoken_get(client, st_user):
    valid_credentials = base64.b64encode(b'st_user:password').decode("utf-8")
    response = client.get('/api/v1/users/get_token/', headers={"Authorization": "Basic " + valid_credentials})
    assert response.status_code == 200
    assert response.json['token'] is not None
    assert User.verify_auth_token(response.json['token']) is st_user


def test_users_gettoken_get_with_invalid_cred(client, st_user):
    invalid_credentials = base64.b64encode(b'st_user:passwordd').decode("utf-8")
    response = client.get('/api/v1/users/get_token/', headers={"Authorization": "Basic " + invalid_credentials})
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid credentials'

    response = client.get('/api/v1/users/get_token/')
    assert response.status_code == 401
    assert response.json['message'] == 'Invalid credentials'


def test_singleuser_get(client, st_user):
    response = client.get(f'/api/v1/users/{st_user.id}', follow_redirects=True)
    assert response.status_code == 200
    assert response.json['username'] == st_user.username


def test_singleuser_put(client, st_user):
    valid_credentials = base64.b64encode(b'st_user:password').decode("utf-8")
    response = client.get('/api/v1/users/get_token/', headers={"Authorization": "Basic " + valid_credentials})
    assert response.status_code == 200

    response = client.put(f'/api/v1/users/{st_user.id}/',
                          headers={"Authorization": "Bearer " + response.json['token']},
                          json={'first_name': 'test', 'gender': 'М'})
    assert response.status_code == 200
    assert st_user.info.first_name == 'test'
    assert st_user.info.gender == 'М'

    token2 = User(username='user2', password='password', email='email@mail.ru').new().generate_auth_token()
    response = client.put(f'/api/v1/users/{st_user.id}/',
                          headers={"Authorization": "Bearer " + token2},
                          json={'first_name': 'user2', 'gender': 'М'})
    assert response.status_code == 403
    assert st_user.info.first_name != 'user2'


def test_singleuser_articles_get(client, st_user, st_article):
    response = client.get(f'/api/v1/users/{st_user.id}/articles/')
    assert response.status_code == 200
    assert response.json['articles'][0]['title'] == st_article.title
    assert len(response.json['articles']) == st_user.count_articles


def test_singleuser_comments_get(client, st_user, st_article, st_comment):
    response = client.get(f'/api/v1/users/{st_user.id}/comments/')
    assert response.status_code == 200
    assert response.json['comments'][0]['url'] == st_comment.url
    assert len(response.json['comments']) == st_user.count_comments
    assert response.json['comments'][0]['article_url'] == st_comment.article.url


def test_articles_get(client, st_article):
    response = client.get('/api/v1/articles/')
    assert response.status_code == 200
    data = response.json['articles']
    articles = Article.query.all()
    for i, article in enumerate(articles):
        assert data[i]['title'] == articles[i].title
        assert data[i]['intro'] == articles[i].intro
        assert data[i]['url'] == articles[i].url


def test_articles_post(client, st_token, st_user):
    assert not st_user.articles
    response = client.post('/api/v1/articles/',
                           json={'title': 'API Title', 'intro': 'API Intro',
                                 'text': 'API Text with at least 30 characters long', 'able_to_comment': False},
                           headers={"Authorization": "Bearer " + st_token})
    assert response.status_code == 200
    assert st_user.articles
    assert st_user.articles[0].title == 'API Title'


def test_singlearticle_get(client, st_article):
    response = client.get(f'/api/v1/articles/{st_article.id}', follow_redirects=True)
    assert response.status_code == 200
    assert response.json['text'] == st_article.text
    assert response.json['id'] == st_article.id


def test_singlearticle_put(client, st_article, st_token, st_token2):
    response = client.put(f'/api/v1/articles/{st_article.id}/',
                          headers={"Authorization": "Bearer " + st_token},
                          json={'title': 'UPDATE API TITLE',
                                'text': 'UPDATE API TEXT WITH AT LEAST 30 CHARACTERS LONG'})
    assert response.status_code == 200
    assert st_article.title == 'UPDATE API TITLE'
    assert st_article.text == 'UPDATE API TEXT WITH AT LEAST 30 CHARACTERS LONG'

    response = client.put(f'/api/v1/articles/{st_article.id}/',
                          headers={"Authorization": "Bearer " + st_token2},
                          json={'title': 'UPDATE API 1234567890 TITLE',
                                'text': 'UPDATE API TEXT WITH 1234567890 AT LEAST 30 CHARACTERS LONG'})

    assert response.status_code == 403
    assert st_article.title == 'UPDATE API TITLE'
    assert st_article.text == 'UPDATE API TEXT WITH AT LEAST 30 CHARACTERS LONG'


def test_singlearticle_delete(client, st_article, st_token, st_token2):
    assert db.session.query(Article).filter_by(id=st_article.id).first() is not None
    response = client.delete(f'/api/v1/articles/{st_article.id}/',
                             headers={"Authorization": "Bearer " + st_token2})
    assert response.status_code == 403
    assert db.session.query(Article).filter_by(id=st_article.id).first() is not None
    response = client.delete(f'/api/v1/articles/{st_article.id}/',
                             headers={"Authorization": "Bearer " + st_token})
    assert response.status_code == 200
    assert db.session.query(Article).filter_by(id=st_article.id).first() is None


def test_singlearticle_comments_get(client, st_article, st_comment):
    response = client.get(f'/api/v1/articles/{st_article.id}/comments/')
    assert response.status_code == 200
    assert len(response.json['comments']) == len(st_article.comments)
    assert response.json['comments'][0]['url'] == st_comment.url


def test_singlearticle_comments_post(client, st_user, st_token, st_article, st_comment):
    response = client.post(f'/api/v1/articles/{st_article.id}/comments/',
                           headers={"Authorization": "Bearer " + st_token},
                           json={'text': 'API COMMENT HERE'})
    assert response.status_code == 200
    comment = db.session.query(Comment).filter_by(text='API COMMENT HERE').first()
    assert comment is not None
    assert comment.url == response.json['url']
    assert comment.article_id == st_article.id
    assert comment.author_id == st_user.id


def test_comments_get(client):
    response = client.get('/api/v1/comments/')
    assert response.status_code == 200
    data = response.json['comments']
    comments = Comment.query.all()
    for i, comment in enumerate(comments):
        assert data[i]['text'] == comment[i].text
        assert data[i]['url'] == comment[i].url


def test_singlecomment_get(client, st_comment):
    response = client.get(f'/api/v1/comments/{st_comment.id}', follow_redirects=True)
    assert response.status_code == 200
    assert response.json['url'] == st_comment.url


def test_singlecomment_put(client, st_comment, st_token, st_token2):
    response = client.put(f'/api/v1/comments/{st_comment.id}', follow_redirects=True,
                          headers={"Authorization": "Bearer " + st_token2},
                          json={'text': 'UPDATED COMMENT API'})
    assert response.status_code == 403

    response = client.put(f'/api/v1/comments/{st_comment.id}', follow_redirects=True,
                          headers={"Authorization": "Bearer " + st_token},
                          json={'text': 'UPDATED COMMENT API'})
    assert response.status_code == 200
    assert response.json['url'] == st_comment.url
    assert response.json['text'] == 'UPDATED COMMENT API'
    assert st_comment.text == 'UPDATED COMMENT API'


def test_singlecomment_delete(client, st_user, st_comment, st_token, st_token2):
    response = client.delete(f'/api/v1/comments/{st_comment.id}', follow_redirects=True,
                             headers={"Authorization": "Bearer " + st_token2})
    assert response.status_code == 403

    response = client.delete(f'/api/v1/comments/{st_comment.id}', follow_redirects=True,
                             headers={"Authorization": "Bearer " + st_token})
    assert response.status_code == 200
    assert not st_user.comments
