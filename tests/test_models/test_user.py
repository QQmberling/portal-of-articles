import time
from datetime import datetime

import pytest

from app.models import User, UserInfo


def test_user_new(st_user):
    user1 = User(username='user1', password='test_pass')
    user2 = User(username='user2', password='test_pass', email='user@mail.ru')
    user1.new()
    user2.new()
    assert user1.username == 'user1'
    assert user1.password_hash is not None
    assert user1.id == user1.info.id
    assert user2.username == 'user2'
    assert user2.password_hash is not None
    assert user2.id == user2.info.id
    assert user2.email == 'user@mail.ru'
    assert user2.password_hash != user1.password_hash


def test_user_create(st_user):
    json = {'username': 'test_user1', 'password': 'password3', 'email': 'user1@gmail.com'}
    user1 = User.create(json)
    json = {'username': 'test_user2', 'password': 'password4', 'email': 'user2@gmail.com'}
    user2 = User.create(json)
    assert user1.email == 'user1@gmail.com'
    assert user2.email == 'user2@gmail.com'
    assert user1.username == 'test_user1'
    assert user1.password_hash is not None
    assert user1.id == user1.info.id
    assert user2.id == user2.info.id
    assert user2.username == 'test_user2'
    assert user2.password_hash is not None


def test_user_delete(st_user):
    user = User(username='username', password='password').new()
    assert User.query.get(user.id) is not None
    assert UserInfo.query.get(user.id) is not None
    user.delete()
    assert User.query.get(user.id) is None
    assert UserInfo.query.get(user.id) is None


def test_user_upd(st_user):
    assert st_user.username == 'st_user'
    st_user.upd({'first_name': 'Alexey', 'last_name': 'Ivanov', 'gender': 'М', 'about': 'Very smart person'})
    assert st_user.info.first_name == 'Alexey'
    assert st_user.info.last_name == 'Ivanov'
    assert st_user.info.gender == 'М'
    assert st_user.info.about == 'Very smart person'
    st_user.upd({'about': 'not so smart actually'})
    assert st_user.info.first_name == 'Alexey'
    assert st_user.info.last_name == 'Ivanov'
    assert st_user.info.gender == 'М'
    assert st_user.info.about == 'not so smart actually'


def test_password_setter(st_user):
    u = User(password='cat')
    assert u.password_hash is not None


def test_no_password_getter(st_user):
    u = User(password='cat')
    with pytest.raises(AttributeError):
        u.password


def test_password_verification(st_user):
    u = User(password='cat')
    assert u.verify_password('cat')
    assert not u.verify_password('dog')


def test_password_salts_are_random(st_user):
    u = User(password='cat')
    u2 = User(password='cat')
    assert u.password_hash != u2.password_hash


def test_generate_auth_token(st_user):
    u = User(username='cat', password='cat').new()
    token = u.generate_auth_token()
    assert u.verify_auth_token(token)


def test_invalid_confirmation_token(st_user):
    u1 = User(username='cat', password='cat').new()
    u2 = User(username='dog', password='dog').new()
    token = u1.generate_auth_token()
    assert u2 != User.verify_auth_token(token)
    assert u1 == User.verify_auth_token(token)
    assert User.verify_auth_token(
        '43u9jer0e[r54ewt09wipo4rj32j4j;re1324piurwepofsdu90p[!%@^#*((*#@)$#)$(*%opsfdi') is None


def test_expiration_confirmation_token(st_user):
    cat = User(username='cat', password='cat').new()
    dog = User(username='dog', password='dog').new()
    token_cat = cat.generate_auth_token(1)
    token_dog = dog.generate_auth_token(3)
    time.sleep(2)
    assert User.verify_auth_token(token_cat) is None
    assert User.verify_auth_token(token_dog) is dog


def test_timestamps(st_user):
    u = User(username='cat', password='cat').new()
    assert (datetime.utcnow() - u.info.date).total_seconds() < 3
    assert (datetime.utcnow() - u.info.last_seen).total_seconds() < 3


def test_avatar(test_request):
    u = User(username='cat', password='cat').new()
    assert '/static/profile_pics/defaults/default' in u.url_avatar
