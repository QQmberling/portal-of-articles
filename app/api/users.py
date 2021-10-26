from flask import jsonify, request, g
from .authentication import token_auth
from . import api
from .errors import bad_request, forbidden
from ..models import User, UserInfo
from .. import db


@api.route('/users/')
def all_users():
    users = User.get_users()
    return jsonify({'users': [user.to_json() for user in users]})


@api.route('/authors/')
def all_authors():
    authors = User.get_authors()
    return jsonify({'authors': [author.to_json() for author in authors]})


@api.route('/users/<int:id>')
def get_user(id):
    try:
        user = User.query.get_or_404(id)
    except:
        return bad_request("user doesn't exist")
    return jsonify(user.to_json())


@api.route('/users/<int:id>/articles/')
def get_user_articles(id):
    try:
        user = User.query.get_or_404(id)
    except:
        return bad_request("user doesn't exist")
    articles = user.articles
    return jsonify({'articles': [article.to_json() for article in articles]})


@api.route('/users/<int:id>/comments/')
def get_user_comments(id):
    try:
        user = User.query.get_or_404(id)
    except:
        return bad_request("user doesn't exist")
    comments = user.comments
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/users/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_user(id):
    try:
        user = User.query.get_or_404(id)
    except:
        return bad_request("user doesn't exist")
    if g.current_user.id != id:
        return forbidden(f'you aren\'t user with id={id}')
    fields = User.api_fields()
    userinfo = UserInfo.query.filter(UserInfo.id == id)
    json = request.get_json()
    for key in json:
        if key not in fields:
            db.session.remove()
            return bad_request(f'field "{key}" doesn\'t exist or can\'t be changed')
        try:
            userinfo.update({key: json[key]})
        except:
            db.session.remove()
            return bad_request(f'not valid data at "{key}" field')
    db.session.commit()
    return user.to_json()
