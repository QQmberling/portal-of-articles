from flask import request, g
from flask_restx import Resource, fields
from werkzeug.datastructures import FileStorage

from . import np_user
from .articles import articles_list_fields
from .authentication import token_auth
from .comments import comments_list_fields
from .validators import str_with_min_length, str_with_max_length, email, username
from ..models import User

user_fields = np_user.model('User', {
    'id': fields.Integer(required=True),
    'url': fields.String(required=True),
    'username': fields.String(required=True),
    'email': fields.String(required=True),
    'first_name': fields.String(required=True, attribute=lambda x: x.info.first_name),
    'last_name': fields.String(required=True, attribute=lambda x: x.info.last_name),
    'gender': fields.String(required=True, attribute=lambda x: x.info.gender),
    'about': fields.String(required=True, attribute=lambda x: x.info.about),
    'date': fields.DateTime(required=True, dt_format='rfc822', attribute=lambda x: x.info.date),
    'last_seen': fields.DateTime(required=True, dt_format='rfc822', attribute=lambda x: x.info.last_seen),
    'count_articles': fields.Integer(required=True),
    'articles': fields.String(required=True, attribute=lambda user: [art.url for art in user.articles]),
    'count_comments': fields.Integer(required=True),
    'comments': fields.String(required=True, attribute=lambda user: [comment.url for comment in user.comments]),
})

users_list_fields = np_user.model('UserList', {
    'users': fields.List(fields.Nested(user_fields))
})

user_parser = np_user.parser()
user_parser.add_argument('first_name', location=['json', 'form'], type=str_with_max_length(30))
user_parser.add_argument('last_name', location=['json', 'form'], type=str_with_max_length(30))
user_parser.add_argument('gender', location=['json', 'form'], choices=('М', 'Ж'), help='Bad choice. Available: (М, Ж).')
user_parser.add_argument('about', location=['json', 'form'], type=str_with_max_length(230))
user_parser.add_argument('avatar', location='files', type=FileStorage)

registration_parser = np_user.parser()
registration_parser.add_argument('email', location='json', type=email(), required=True)
registration_parser.add_argument('username', location='json', type=username(), required=True)
registration_parser.add_argument('password', location='json', type=str_with_min_length(4), required=True)


@np_user.route("/")
class Users(Resource):
    @np_user.marshal_list_with(users_list_fields)
    def get(self):
        users = User.query.all()
        return {'users': users}

    @np_user.expect(registration_parser)
    @np_user.marshal_with(user_fields)
    def post(self):
        args = registration_parser.parse_args(strict=True)
        payload = request.get_json()
        user = User.create(payload)
        return user


@np_user.route("/authors/")
class Authors(Resource):
    @np_user.marshal_list_with(users_list_fields)
    def get(self):
        users = User.get_authors()
        return {'users': users}


@np_user.route("/<int:id>/")
@np_user.param("id", "The user identifier")
class SingleUser(Resource):
    @np_user.marshal_with(user_fields)
    def get(self, id):
        user = User.query.get_or_404(id)
        return user

    @token_auth.login_required
    @np_user.doc(security='apikey')
    @np_user.expect(user_parser)
    @np_user.marshal_with(user_fields)
    def put(self, id):
        user = User.query.get_or_404(id)
        if g.current_user.id != user.id:
            np_user.abort(403)
        args = user_parser.parse_args(strict=True)
        args = dict(args)
        payload = {k: v for k, v in args.items() if v is not None}
        if not payload:
            np_user.abort(400, message='Empty request.')
        user = user.upd(payload)
        return user


@np_user.route('/<int:id>/articles/')
@np_user.param("id", "The user identifier")
class UserArticles(Resource):
    @np_user.marshal_list_with(articles_list_fields)
    def get(self, id):
        user = User.query.get_or_404(id)
        articles = user.articles
        return {'articles': articles}


@np_user.route('/<int:id>/comments/')
@np_user.param("id", "The user identifier")
class UserComments(Resource):
    @np_user.marshal_list_with(comments_list_fields)
    def get(self, id):
        user = User.query.get_or_404(id)
        comments = user.comments
        return {'comments': comments}
