from flask import jsonify, request, g
from . import api
from .authentication import token_auth
from .errors import bad_request
from .. import db
from ..models import Comment, Article


@api.route('/comments/')
def all_comments():
    comments = Comment.get_comments()
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/comments/<int:id>')
def get_comment(id):
    try:
        comment = Comment.query.get_or_404(id)
    except:
        return bad_request("comment doesn't exist")
    return jsonify(comment.to_json())


@api.route('/articles/<int:id>/comments', methods=['POST'])
@token_auth.login_required
def new_comment(id):
    try:
        article = Article.query.get_or_404(id)
    except:
        return bad_request("article doesn't exist")
    comment = Comment.from_json(request.get_json(), id, g.current_user.id)
    db.session.add(comment)
    db.session.commit()
    return jsonify(comment.to_json())
