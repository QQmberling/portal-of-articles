import os
import sqlite3
from datetime import datetime

from flask import render_template, request, redirect, flash, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.datastructures import MultiDict

from app import TIMEZONE, PROFILE_PIC_NAME
from app.classes import User, Article, UserInfo, Comment
from app.image import scale_image
from . import main
from .forms import LoginForm, RegistrationForm, ArticleCreateForm, ArticleEditForm, UserEditForm, ImageForm, \
    CreateCommentForm
from .. import db, login_manager


def sort_authors(authors):
    N = len(authors)
    for i in range(N-1):
        for j in range(N-i-1):
            if len(authors[j][0].articles) < len(authors[j+1][0].articles):
                authors[j], authors[j+1] = authors[j+1], authors[j]
    return authors


def save_image(picture_file):
    picture_ext = f".{picture_file.filename.split('.')[-1]}"
    picture_name = f'{PROFILE_PIC_NAME}{str(current_user.id)}{picture_ext}'

    temp_path = os.path.join(main.root_path, '../static/temp_pics', picture_name)
    picture_file.save(temp_path)

    picture_path = os.path.join(main.root_path, '../static/profile_pics', picture_name)  # Путь для картинки профиля (для отображения в профиле)
    picture_path2 = os.path.join(main.root_path, '../static/other_profile_pics', picture_name)  # Путь для картинки профиля уменьшенной версии (для остального)

    scale_image(temp_path, picture_path, target=True)
    scale_image(temp_path, picture_path2, target=False)

    if os.path.isfile(temp_path):
        os.remove(temp_path)
    else:
        print("File doesn't exists!")

    return picture_name


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


# @main.before_first_request
# def before_first_request():
#     pass


@main.before_request
def update_last_active():
    current_user.last_seen = datetime.now(TIMEZONE)
    db.session.commit()


@main.after_request
def after_request(response):
    return response


@main.route('/profile')
@login_required
def profile():
    context = {'legend': f'Профиль {current_user.username}'}
    articles = db.session.query(Article).filter(Article.author_id == current_user.id).all()
    return render_template('profile.html', context=context, articles=articles)


@main.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def profile_edit():
    context = {'legend': f'Профиль {current_user.username}'}
    if request.method == 'GET':
        form = UserEditForm(MultiDict({'first_name': current_user.info.first_name,
                                       'last_name': current_user.info.last_name,
                                       'about': current_user.info.about,
                                       'gender': current_user.info.gender
                                       }))
        form2 = ImageForm()
    else:
        form = UserEditForm()
        form2 = ImageForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        about = form.about.data
        gender = form.gender.data

        current_user.info.about = about
        current_user.info.first_name = first_name
        current_user.info.last_name = last_name
        current_user.info.gender = gender

        form2.avatar.data = form.avatar.data
        if form2.validate_on_submit():
            picture_name = save_image(form.avatar.data)
            current_user.picture_name = picture_name
        else:
            if form2.avatar.data.stream.name is not None:
                flash('Аватар не соответствует требованиям.', 'danger')
                return render_template('profile_edit.html', context=context, form=form, form2=form2)

            if current_user.picture_name == 'default_male.png' or current_user.picture_name == 'default_female.png':
                if current_user.info.gender == 'М':
                    current_user.picture_name = 'default_male.png'
                else:
                    current_user.picture_name = 'default_female.png'

        db.session.commit()
        return redirect(url_for('.profile'))

    return render_template('profile_edit.html', context=context, form=form, form2=form2)


@main.route('/profile/<string:username>', methods=['POST', 'GET'])
def profile_with_login(username):
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for('.profile'))
    profile_user = db.session.query(User).filter_by(username=username).first_or_404()
    context = {'legend': f'Профиль {username}'}
    return render_template('profile_with_login.html',
                           context=context,
                           profile_user=profile_user)


@main.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('.index'))


@main.route('/register', methods=['POST', 'GET'])
def register():
    context = {'legend': 'Регистрация'}
    if current_user.is_authenticated:
        return redirect(url_for('.profile'))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        new_user = User(username=username, password=password, email=email, date=datetime.now(TIMEZONE))
        try:
            db.session.add(new_user)
            db.session.commit()
            id = db.session.query(User.id).filter_by(username=username).first()[0]
            user_info = UserInfo(id=id)
            db.session.add(user_info)
            db.session.commit()
            flash(f'Регистрация аккаунт на email {email} успешно завершена. Можете авторизоваться.', 'success')
        except sqlite3.Error as e:
            return f'При регистрации возникла ошибка {e}'
        return redirect(url_for('.login_form'))
    return render_template('register.html', context=context, form=form)


@main.route('/')
@main.route('/home')
def index():
    context = {'legend': 'Главная'}
    return render_template('index.html', context=context)


@main.route('/posts')
def posts():
    context = {'legend': 'Статьи'}
    content = db.session.query(Article, User).filter(Article.author_id == User.id).all()
    return render_template('posts.html', content=content, context=context)


@main.route('/posts/<int:id>', methods=['POST', 'GET'])
def post_detail(id):
    form = None
    context = {'legend': ''}
    content = db.session.query(Article, User).filter(Article.id == id).filter(Article.author_id == User.id).first_or_404()

    if request.method == 'POST':
        if current_user.is_authenticated:
            form = CreateCommentForm()
            if form.validate_on_submit():
                comment = Comment(text=form.text.data, author_id=current_user.id, article_id=id, date=datetime.now(TIMEZONE))
                db.session.add(comment)
                db.session.commit()
                return redirect(url_for('.post_detail', id=id))
        else:
            session['next'] = url_for('.post_detail', id=id)
            return redirect(url_for('.login_form'))

    return render_template('post_detail.html', content=content, context=context, form=form)


@main.route('/posts/<int:id>/del')
@login_required
def post_delete(id):
    article = Article.query.get_or_404(id)
    if current_user.id == article.author_id:
        try:
            db.session.delete(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'При удалении статьи произошла ошибка'
    else:
        return 'Статью может удалять только автор'


@main.route('/comment/<int:id>/del')
@login_required
def comment_delete(id):
    comment = Comment.query.get_or_404(id)
    if current_user.id == comment.author_id:
        try:
            db.session.delete(comment)
            db.session.commit()
            return redirect(url_for('.post_detail', id=comment.article_id))
        except:
            return 'При удалении комментария произошла ошибка'
    else:
        return 'Комментарий может удалять только автор'


@main.route('/create-article', methods=['POST', 'GET'])
@login_required
def create_article():
    context = {'legend': 'Создание статьи'}

    form = ArticleCreateForm()

    if form.validate_on_submit():
        title = form.title.data
        intro = form.intro.data
        text = form.text.data
        able_to_comment = form.able_to_comment.data

        new_article = Article(title=title,
                              intro=intro,
                              text=text,
                              able_to_comment=able_to_comment,
                              author_id=current_user.id,
                              date=datetime.now(TIMEZONE))

        try:
            db.session.add(new_article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'При добавлении статьи возникла ошибка'
    return render_template('create-article.html', context=context, form=form)


@main.route('/posts/<int:id>/update', methods=['POST', 'GET'])
@login_required
def post_update(id):
    context = {'legend': 'Редактирование статьи'}

    article = Article.query.get_or_404(id)
    if current_user.id == article.author_id:
        if request.method == 'GET':
            form = ArticleEditForm(MultiDict({'title': article.title, 'intro': article.intro, 'text': article.text, 'able_to_comment': article.able_to_comment}))
        else:
            form = ArticleEditForm()

        if form.validate_on_submit():
            article.title = form.title.data
            article.intro = form.intro.data
            article.text = form.text.data
            article.able_to_comment = form.able_to_comment.data
            article.edit_date = datetime.now(TIMEZONE)
            try:
                db.session.commit()
                return redirect('/posts')
            except:
                return 'При редактировании статьи возникла ошибка'
        else:
            return render_template('post_update.html', context=context, form=form)
    else:
        return 'Обновлять статью может только её автор'


@main.route("/login_form", methods=["POST", "GET"])
def login_form():
    context = {'legend': 'Авторизация'}
    if current_user.is_authenticated:
        return redirect(url_for('.index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and user.verify_password(password):
            rm = form.remember.data
            login_user(user, remember=rm)
            next = session.pop('next', None)
            return redirect(request.args.get("next") or next or url_for(".index"))
        else:
            flash('Неверный логин или пароль', category='danger')
    return render_template('login_form.html', context=context, form=form)


@main.route('/authors', methods=["POST", "GET"])
def authors_page():
    context = {'legend': 'Авторы'}
    authors = db.session.query(User, UserInfo).filter(User.id == UserInfo.id).all()
    authors = sort_authors(authors)
    return render_template('authors.html', context=context, authors=authors)


@main.route('/prank/<int:id>')
def prank(id):
    flash('Редачить комменты пока нельзя =(((((', 'danger')
    return redirect(url_for('.post_detail', id=id))


