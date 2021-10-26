from datetime import datetime

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth

from .. import TIMEZONE, db
from ..models import User
from . import api
from .errors import unauthorized, forbidden

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
def verify_password(email, password):
    if email == '':
        return False
    user = User.query.filter_by(email=email.lower()).first()
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)


@api.route('/tokens/')
@basic_auth.login_required
def get_token():
    if g.current_user.is_anonymous:
        return unauthorized('Invalid credentials')
    token = g.current_user.generate_auth_token(expiration=3600)
    return jsonify({'token': token, 'expiration': 3600})


@token_auth.verify_token
def verify_token(token):
    g.current_user = User.verify_auth_token(token)
    if g.current_user is not None:
        g.current_user.last_seen = datetime.now(TIMEZONE)
        db.session.commit()
    return g.current_user is not None

