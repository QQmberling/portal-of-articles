from flask import jsonify, request, g, url_for
from . import api
from .errors import bad_request, forbidden
from ..models import Article
from .authentication import token_auth
from .. import db


@api.route('/articles/')
def all_articles():
    articles = Article.get_articles()
    return jsonify({'articles': [article.to_json() for article in articles]})


@api.route('/articles/<int:id>')
def get_article(id):
    try:
        article = Article.query.get_or_404(id)
    except:
        return bad_request("article doesn't exist")
    return jsonify(article.to_json())


@api.route('/articles/<int:id>/comments/')
def get_article_comments(id):
    try:
        article = Article.query.get_or_404(id)
    except:
        return bad_request("article doesn't exist")
    comments = article.comments
    return jsonify({'comments': [comment.to_json() for comment in comments]})


@api.route('/articles/', methods=['POST'])
@token_auth.login_required
def new_article():
    article = Article.from_json(request.json, g.current_user.id)
    db.session.add(article)
    db.session.commit()
    return jsonify(article.to_json()), 201


@api.route('/articles/<int:id>', methods=['PUT'])
@token_auth.login_required
def update_article(id):
    try:
        article = Article.query.get_or_404(id)
    except:
        return bad_request("article doesn't exist")
    if article.author_id != g.current_user.id:
        return forbidden(f'you aren\'t author of article with id={id}')
    fields = Article.api_fields()
    article_query = Article.query.filter(Article.id == id)
    json = request.get_json()
    for key in json:
        if key not in fields:
            db.session.remove()
            return bad_request(f'field "{key}" doesn\'t exist or can\'t be changed')
        try:
            article_query.update({key: json[key]})
        except:
            db.session.remove()
            return bad_request(f'not valid data at "{key}" field')
    db.session.commit()
    return jsonify(article.to_json()), 200


@api.route('/articles/<int:id>', methods=['DELETE'])
@token_auth.login_required
def delete_article(id):
    try:
        article = Article.query.get_or_404(id)
    except:
        return bad_request("article doesn't exist")
    if article.author_id != g.current_user.id:
        return forbidden(f'you aren\'t author of article with id={id}')
    db.session.delete(article)
    db.session.commit()
    return jsonify({'status': 'successfully deleted'}), 200
