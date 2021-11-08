from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from flask_restx import Resource

from . import np_user
from .errors import unauthorized
from ..models import User

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth('Bearer')
multi_auth = MultiAuth(basic_auth, token_auth)


@basic_auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@token_auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@basic_auth.verify_password
def verify_password(username, password):
    if username == '':
        return False
    user = User.query.filter_by(username=username).first()
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)


@token_auth.verify_token
def verify_token(token):
    g.current_user = User.verify_auth_token(token)
    if g.current_user is not None:
        g.current_user.ping()
    return g.current_user is not None


@np_user.route('/get_token/')
class Token(Resource):
    @basic_auth.login_required
    @np_user.doc(security='Basic Auth')
    def get(self):
        if g.current_user.is_anonymous:
            return np_user.abort(401)
        token = g.current_user.generate_auth_token(expiration=3600)
        return {'token': token, 'expiration': 3600}
