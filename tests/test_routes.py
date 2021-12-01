import re

from app import db
from app.models import User, Article, Comment


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert 'Главная' in response.get_data(as_text=True)


def test_register_and_authorization(client):
    response = client.post('/register', data={
        'email': 'john@example.com',
        'username': 'john',
        'password': 'catt',
        'confirm_password': 'catt',
    })
    assert response.status_code == 302
    assert db.session.query(User).filter_by(username='john').first() is not None
    assert db.session.query(User).filter_by(username='johnn').first() is None
    assert not re.search('Регистрация аккаунта на email john@example.com успешно завершена. Можете авторизоваться.',
                         response.get_data(as_text=True))

    response = client.post('/register', data={
        'email': 'mike@example.com',
        'username': 'mike',
        'password': 'dogg',
        'confirm_password': 'dogg',
    })
    assert response.status_code == 302

    response = client.post('/login', data={
        'username': 'john',
        'password': 'catt',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert not re.search('Неверный логин или пароль', response.get_data(as_text=True))

    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert re.search('Профиль john', response.get_data(as_text=True))

    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200

    response = client.get('/profile', follow_redirects=True)
    assert response.status_code == 200
    assert not re.search('Профиль john', response.get_data(as_text=True))
    assert re.search('Необходимо авторизоваться', response.get_data(as_text=True))

    response = client.post('/login', data={
        'username': 'john',
        'password': 'catT',
    }, follow_redirects=True)
    assert response.status_code == 200
    assert re.search('Неверный логин или пароль', response.get_data(as_text=True))


def test_profile_edit(logged_john):
    response = logged_john.get('/profile/edit', follow_redirects=True)
    assert response.status_code == 200

    response = logged_john.post('/profile/edit', data={
        'first_name': 'john',
        'last_name': 'freeman',
        'gender': 'Ж',
        'about': 'Very smart person',
    }, follow_redirects=True)
    assert response.status_code == 200
    user = db.session.query(User).filter_by(username='john').first()
    assert user.info.first_name == 'john'
    assert user.info.last_name == 'freeman'
    assert user.info.gender == 'Ж'
    assert user.info.about == 'Very smart person'
    assert re.search('john', response.get_data(as_text=True))
    assert re.search('freeman', response.get_data(as_text=True))
    assert re.search('Very smart person', response.get_data(as_text=True))


def test_create_article(logged_john):
    response = logged_john.post('/create-article', data={
        'title': 'John Title',
        'intro': 'John Intro',
        'text': 'Джон Стори (англ. John Storey; род. 19 июля 1987[1][2], Кембридж) — новозеландский гребец английского происхождения, выступающий за сборную Новой Зеландии по академической гребле с 2009 года. Чемпион мира, победитель этапов Кубка мира, участник двух летних Олимпийских игр.',
        'able_to_comment': True,
    }, follow_redirects=True)
    assert response.status_code == 200
    article = db.session.query(Article).filter_by(title='John Title').first()
    assert article.intro == 'John Intro'
    assert article.text == 'Джон Стори (англ. John Storey; род. 19 июля 1987[1][2], Кембридж) — новозеландский гребец английского происхождения, выступающий за сборную Новой Зеландии по академической гребле с 2009 года. Чемпион мира, победитель этапов Кубка мира, участник двух летних Олимпийских игр.'
    assert re.search('John Title', response.get_data(as_text=True))


def test_update_article(logged_john):
    article = db.session.query(Article).filter_by(title='John Title').first()
    response = logged_john.post(f'/articles/{article.id}/update', data={
        'title': 'John Title EDITED',
        'intro': 'John Intro: EDITED',
        'text': 'Джон Стори (англ. John Storey; род. 19 июля 1987[1][2], Кембридж) — новозеландский гребец английского происхождения, выступающий за сборную Новой Зеландии по академической гребле с 2009 года. Чемпион мира, победитель этапов Кубка мира, участник двух летних Олимпийских игр.',
        'able_to_comment': False,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert article.title == 'John Title EDITED'
    assert article.intro == 'John Intro: EDITED'
    assert article.text == 'Джон Стори (англ. John Storey; род. 19 июля 1987[1][2], Кембридж) — новозеландский гребец английского происхождения, выступающий за сборную Новой Зеландии по академической гребле с 2009 года. Чемпион мира, победитель этапов Кубка мира, участник двух летних Олимпийских игр.'
    assert re.search('John Title EDITED', response.get_data(as_text=True))


def test_create_comment_without_login(client):
    article = db.session.query(Article).filter_by(title='John Title EDITED').first()
    response = client.post(f'/articles/{article.id}', data={'text': 'that comment will never be'},
                           follow_redirects=True)
    assert response.status_code == 200
    assert re.search('Необходимо авторизоваться', response.get_data(as_text=True))
    comment = db.session.query(Comment).filter_by(text='that comment will never be').first()
    assert comment is None


def test_make_comment(logged_mike):
    article = db.session.query(Article).filter_by(title='John Title EDITED').first()
    response = logged_mike.post(f'/articles/{article.id}', data={'text': 'Mike\'s comment'}, follow_redirects=True)
    comment = db.session.query(Comment).filter_by(text='Mike\'s comment').first()
    assert comment is not None
    assert comment.author.username == 'mike'
    assert comment.article_id == article.id


def test_delete_comment_by_not_author(logged_john):
    comment = db.session.query(Comment).filter_by(text='Mike\'s comment').first()
    response = logged_john.get(f'/comment/{comment.id}/delete', follow_redirects=True)
    assert response.status_code == 403
    assert re.search('Ошибка №403', response.get_data(as_text=True))
    comment = db.session.query(Comment).filter_by(text='Mike\'s comment').first()
    assert comment is not None


def test_delete_comment(logged_mike):
    comment = db.session.query(Comment).filter_by(text='Mike\'s comment').first()
    response = logged_mike.get(f'/comment/{comment.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    assert re.search('John Title EDITED', response.get_data(as_text=True))
    comment = db.session.query(Comment).filter_by(text='Mike\'s comment').first()
    assert comment is None


def test_articles_page(client):
    response = client.get('/articles', follow_redirects=True)
    assert response.status_code == 200
    articles = db.session.query(Article).all()
    for art in articles:
        assert re.search(art.title, response.get_data(as_text=True))


def test_author_page(client):
    response = client.get('/authors', follow_redirects=True)
    assert response.status_code == 200
    authors = User.get_authors()
    for author in authors:
        assert re.search(author.username, response.get_data(as_text=True))


def test_delete_article_by_not_author(logged_mike):
    article = db.session.query(Article).filter_by(title='John Title EDITED').first()
    assert article is not None
    response = logged_mike.get(f'/articles/{article.id}/delete', follow_redirects=True)
    assert response.status_code == 403
    assert re.search('Ошибка №403', response.get_data(as_text=True))
    article = db.session.query(Article).filter_by(title='John Title EDITED').first()
    assert article is not None


def test_delete_article(logged_john):
    article = db.session.query(Article).filter_by(title='John Title EDITED').first()
    assert article is not None
    response = logged_john.get(f'/articles/{article.id}/delete', follow_redirects=True)
    assert response.status_code == 200
    article = db.session.query(Article).filter_by(title='John Title EDITED').first()
    assert article is None


def test_profile_with_login(logged_john):
    user2 = db.session.query(User).filter_by(username='mike').first()
    response = logged_john.get(f'/profile/{user2.username}', follow_redirects=True)
    assert response.status_code == 200
    assert re.search('Профиль mike', response.get_data(as_text=True))
    assert not re.search('Редактировать профиль', response.get_data(as_text=True))

    response = logged_john.get('/profile/john', follow_redirects=True)
    assert response.status_code == 200
    assert re.search('Редактировать профиль', response.get_data(as_text=True))


def test_index_page(client):
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200


def test_create_article_without_login(client):
    response = client.post('/create-article', data={
        'title': 'The Title will never be',
        'intro': 'The Intro will never be',
        'text': 'The Text will never be',
        'able_to_comment': True,
    }, follow_redirects=True)
    assert response.status_code == 200
    assert re.search('Необходимо авторизоваться', response.get_data(as_text=True))
    article = db.session.query(Article).filter_by(title='The Title will never be').first()
    assert article is None


def test_ping_user(logged_john):
    user = db.session.query(User).filter_by(username='john').first()
    last_seen_previos = user.info.last_seen
    assert last_seen_previos > user.info.date
    response = logged_john.get('/', follow_redirects=True)
    assert user.info.last_seen > last_seen_previos
