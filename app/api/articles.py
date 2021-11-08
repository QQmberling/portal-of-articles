from flask import g, request
from flask_restx import fields, Resource
from flask_restx.inputs import boolean

from . import np_art
from .authentication import token_auth
from .comments import comments_list_fields, comment_fields, comment_parser
from .validators import str_with_min_length
from ..models import Article, Comment

article_fields = np_art.model('Article', {
    'id': fields.Integer(required=True),
    'url': fields.String(required=True),
    'title': fields.String(required=True),
    'intro': fields.String(required=True),
    'text': fields.String(required=True),
    'date': fields.DateTime(required=True, dt_format='rfc822'),
    'edit_date': fields.DateTime(required=True, dt_format='rfc822'),
    'able_to_comment': fields.Boolean(),
    'author_id': fields.String(required=True),
    'author_url': fields.String(required=True),
    'comments': fields.String(required=True, attribute=lambda article: [comment.url for comment in article.comments]),
})

article_fields_short = np_art.model('ArticleShort', {
    'id': fields.Integer(required=True),
    'url': fields.String(required=True),
    'title': fields.String(required=True),
    'intro': fields.String(required=True),
    'date': fields.DateTime(required=True, dt_format='rfc822'),
})

articles_list_fields = np_art.model('ArticlesList', {
    'articles': fields.List(fields.Nested(article_fields_short)),
})

article_parser = np_art.parser()
article_parser.add_argument('title', location='json', type=str_with_min_length(1), required=True)
article_parser.add_argument('intro', location='json', type=str_with_min_length(4), required=True)
article_parser.add_argument('text', location='json', type=str_with_min_length(30), required=True)
article_parser.add_argument('able_to_comment', location='json', type=boolean)

article_parser_updating = np_art.parser()
article_parser_updating.add_argument('title', location='json', type=str_with_min_length(1))
article_parser_updating.add_argument('intro', location='json', type=str_with_min_length(4))
article_parser_updating.add_argument('text', location='json', type=str_with_min_length(30))
article_parser_updating.add_argument('able_to_comment', location='json', type=boolean)


@np_art.route("/")
class Articles(Resource):
    @np_art.marshal_list_with(articles_list_fields)
    def get(self):
        articles = Article.query.all()
        return {'articles': articles}

    @token_auth.login_required
    @np_art.doc(security='apikey')
    @np_art.expect(article_parser)
    @np_art.marshal_with(article_fields)
    def post(self):
        args = article_parser.parse_args(strict=True)
        payload = request.get_json()
        payload['author_id'] = g.current_user.id
        article = Article.create(payload)
        return article


@np_art.route("/<int:id>/")
@np_art.param("id", "The article identifier")
class SingleArticle(Resource):
    @np_art.marshal_with(article_fields)
    def get(self, id):
        article = Article.query.get_or_404(id)
        return article

    @token_auth.login_required
    @np_art.doc(security='apikey')
    @np_art.expect(article_parser_updating)
    @np_art.marshal_with(article_fields)
    def put(self, id):
        article = Article.query.get_or_404(id)
        if g.current_user.id != article.author_id:
            np_art.abort(403)
        args = article_parser_updating.parse_args(strict=True)
        payload = request.get_json()
        article = article.upd(payload)
        return article

    @token_auth.login_required
    @np_art.doc(security='apikey')
    def delete(self, id):
        article = Article.query.get_or_404(id)
        if g.current_user.id != article.author_id:
            np_art.abort(403)
        article.delete()
        return {'message': 'successful deleted'}


@np_art.route('/<int:id>/comments/')
@np_art.param("id", "The article identifier")
class ArticleComments(Resource):
    @np_art.marshal_list_with(comments_list_fields)
    def get(self, id):
        article = Article.query.get_or_404(id)
        comments = article.comments
        return {'comments': comments}

    @token_auth.login_required
    @np_art.doc(security='apikey')
    @np_art.expect(comment_parser)
    @np_art.marshal_with(comment_fields)
    def post(self, id):
        article = Article.query.get_or_404(id)
        args = comment_parser.parse_args(strict=True)
        payload = request.get_json()
        payload['article_id'] = id
        payload['author_id'] = g.current_user.id
        comment = Comment.create(payload)
        return comment
