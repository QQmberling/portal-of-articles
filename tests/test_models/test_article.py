from app import db
from app.models import Article


def test_article_new(st_user):
    article = Article.create({'title': 'Test Article',
                              'intro': 'Test Intro',
                              'text': 'Test Text',
                              'author_id': st_user.id,
                              'able_to_comment': False})
    assert article.id is not None
    assert article.author.username == 'st_user'
    assert article.title == 'Test Article'
    assert article.intro == 'Test Intro'
    assert article.text == 'Test Text'
    assert article.able_to_comment == False
    assert article.date is not None


def test_article_create(st_user):
    article = Article(title='Test Article', intro='Test Intro', text='Test Text', author_id=st_user.id).new()
    assert article.id is not None
    assert article.author.username == 'st_user'
    assert article.title == 'Test Article'
    assert article.intro == 'Test Intro'
    assert article.text == 'Test Text'
    assert article.able_to_comment == True
    assert article.date is not None


def test_article_delete(st_article):
    assert st_article is not None
    st_article.delete()
    article = db.session.query(Article).filter_by(title='st_article').first()
    assert article is None


def test_article_upd(st_article):
    payload = {'title': 'Test Article updated',
               'intro': 'Test Intro updated',
               'text': 'Test Text updated',
               'able_to_comment': False}
    st_article.upd(payload)
    assert st_article.title == 'Test Article updated'
    assert st_article.intro == 'Test Intro updated'
    assert st_article.text == 'Test Text updated'
    assert st_article.able_to_comment == False
    assert st_article.edit_date > st_article.date
