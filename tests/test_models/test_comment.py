from app import db
from app.models import Article, Comment


def test_comment_new(st_user, st_article, st_comment):
    comment = Comment.create({'text': 'Test Comment',
                              'article_id': st_article.id,
                              'author_id': st_user.id,
                              })
    assert comment.id is not None
    assert comment.author.username == 'st_user'
    assert comment.author.id == st_user.id
    assert comment.article.id == st_article.id
    assert comment.text == 'Test Comment'
    assert comment.date is not None
    assert comment.date > st_article.date


def test_comment_create(st_user, st_article, st_comment):
    comment = Comment(text='Test Comment', article_id=st_article.id, author_id=st_user.id).new()
    assert comment.id is not None
    assert comment.author.username == 'st_user'
    assert comment.author.id == st_user.id
    assert comment.article.id == st_article.id
    assert comment.text == 'Test Comment'
    assert comment.date is not None
    assert comment.date > st_article.date


def test_comment_delete(st_comment):
    assert st_comment is not None
    st_comment.delete()
    comment = db.session.query(Article).filter_by(text='st_comment').first()
    assert comment is None


def test_comment_upd(st_comment):
    assert st_comment is not None
    payload = {'text': 'st_comment updated'}
    st_comment.upd(payload)
    comment = db.session.query(Article).filter_by(id=st_comment.id).first()
    assert st_comment.text == 'st_comment updated'
    assert st_comment.edit_date > st_comment.date
