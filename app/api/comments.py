from flask import request, g
from flask_restx import Resource, fields

from . import np_comm
from .authentication import token_auth
from .validators import str_with_min_length
from ..models import Comment

comment_fields = np_comm.model('Comment', {
    'id': fields.Integer(required=True),
    'url': fields.String(required=True),
    'text': fields.String(required=True),
    'date': fields.DateTime(required=True, dt_format='rfc822'),
    'edit_date': fields.DateTime(required=True, dt_format='rfc822'),
    'article_url': fields.String(required=True),
    'author_url': fields.String(required=True),
})

comment_fields_short = np_comm.model('CommentShort', {
    'url': fields.String(required=True),
    'article_url': fields.String(required=True),
})

comments_list_fields = np_comm.model('CommentsList', {
    'comments': fields.List(fields.Nested(comment_fields_short))
})

comment_parser = np_comm.parser()
comment_parser.add_argument('text', location='json', type=str_with_min_length(1), required=True)


@np_comm.route("/")
class Comments(Resource):
    @np_comm.marshal_list_with(comments_list_fields)
    def get(self):
        comments = Comment.query.all()
        return {'comments': comments}


@np_comm.route("/<int:id>/")
@np_comm.param("id", "The comment identifier")
class SingleComment(Resource):
    @np_comm.marshal_with(comment_fields)
    def get(self, id):
        comment = Comment.query.get_or_404(id)
        return comment

    @token_auth.login_required
    @np_comm.doc(security='apikey')
    @np_comm.expect(comment_parser)
    @np_comm.marshal_with(comment_fields)
    def put(self, id):
        comment = Comment.query.get_or_404(id)
        if g.current_user.id != comment.author_id:
            np_comm.abort(403)
        args = comment_parser.parse_args(strict=True)
        payload = request.get_json()
        comment = comment.upd(payload)
        return comment

    @token_auth.login_required
    @np_comm.doc(security='apikey')
    def delete(self, id):
        comment = Comment.query.get_or_404(id)
        if g.current_user.id != comment.author_id:
            np_comm.abort(403)
        comment.delete()
        return {'message': 'successful deleted'}
