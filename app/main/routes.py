from flask import render_template, request, redirect, flash, url_for, session, abort
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.datastructures import MultiDict

from app.models import User, Article, Comment, UserInfo, models
from . import main
from .forms import LoginForm, RegistrationForm, ArticleCreateForm, ArticleEditForm, UserEditForm, CommentCreateForm, DateFilterForm
from .. import db, login_manager
from ..exceptions import ValidationError


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@main.before_request
def update_last_active():
    if not current_user.is_anonymous:
        current_user.ping()


@main.after_request
def after_request(response):
    return response


@main.route('/profile')
@login_required
def profile():
    context = {'legend': f'Профиль {current_user.username}'}
    return render_template('profile.html', context=context)


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
    else:
        form = UserEditForm()
    if form.validate_on_submit():
        payload = {'first_name': form.first_name.data,
                   'last_name': form.last_name.data,
                   'about': form.about.data,
                   'gender': form.gender.data, }
        # if form.avatar.data.stream.name is not None:
        #     payload['avatar'] = form.avatar.data
        if form.avatar.data is not None and form.avatar.data.filename != '':
            payload['avatar'] = form.avatar.data
        try:
            current_user.upd(payload)
        except ValidationError as e:
            flash(f'{e}', 'danger')
            return render_template('profile_edit.html', context=context, form=form)
        return redirect(url_for('.profile'))
    return render_template('profile_edit.html', context=context, form=form)


@main.route('/profile/<string:username>')
def profile_with_login(username):
    if current_user.is_authenticated and current_user.username == username:
        return redirect(url_for('.profile'))
    profile_user = db.session.query(User).filter_by(username=username).first_or_404()
    context = {'legend': f'Профиль {username}', 'profile_user': [profile_user]}
    return render_template('profile_with_login.html', context=context)


@main.route('/logout')
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
        payload = {'email': form.email.data,
                   'username': form.username.data,
                   'password': form.password.data,
                   }
        User.create(payload)
        flash(f'Регистрация аккаунта на email {payload["email"]} успешно завершена. Можете авторизоваться.',
              'success')
        return redirect(url_for('.login'))
    return render_template('register.html', context=context, form=form)


@main.route('/', methods=['POST', 'GET'])
def index():
    form = DateFilterForm()
    context = {'legend': 'Главная'}
    all_instances = []
    if request.method == 'GET':
        all_instances = UserInfo.query.all() + Article.query.all() + Comment.query.all()
    elif form.validate_on_submit():
        for model in models:
            all_instances.extend(model.query.filter(model.date.between(form.date1.data, form.date2.data)).all())
            # all_instances = [el for el in map(lambda x: x if form.date1.data < x.date.date() < form.date2.data else None, all_instances) if el is not None]
    all_instances.sort(key=lambda x: x.date, reverse=True)
    return render_template('index.html', context=context, lst=all_instances, form=form)


@main.route('/articles')
def articles():
    articles = db.session.query(Article).all()
    context = {'legend': 'Статьи', 'articles': articles}
    return render_template('articles.html', context=context)


@main.route('/articles/<int:id>', methods=['POST', 'GET'])
def article_detail(id):
    form = None
    article = db.session.query(Article).filter(Article.id == id).first_or_404()
    if request.method == 'POST':
        if current_user.is_authenticated:
            form = CommentCreateForm()
            if form.validate_on_submit():
                payload = {'text': form.text.data, 'author_id': current_user.id, 'article_id': id}
                Comment.create(payload)
                return redirect(url_for('.article_detail', id=id))
        else:
            flash('Необходимо авторизоваться.', 'danger')
            session['next'] = url_for('.article_detail', id=id)
            return redirect(url_for('.login'))
    context = {'legend': '', 'article': article}
    return render_template('article_detail.html', context=context, form=form)


@main.route('/articles/<int:id>/delete')
@login_required
def article_delete(id):
    article = Article.query.get_or_404(id)
    if current_user.id == article.author_id:
        article.delete()
        return redirect(url_for('.articles'))
    else:
        return abort(403, 'Статью может удалять только автор')


@main.route('/comment/<int:id>/delete')
@login_required
def comment_delete(id):
    comment = Comment.query.get_or_404(id)
    if current_user.id == comment.author_id:
        comment.delete()
        return redirect(url_for('.article_detail', id=comment.article_id))
    else:
        return abort(403, 'Комметарий может удалять только автор')


@main.route('/create-article', methods=['POST', 'GET'])
@login_required
def article_create():
    form = ArticleCreateForm()
    if form.validate_on_submit():
        payload = {'title': form.title.data,
                   'intro': form.intro.data,
                   'text': form.text.data,
                   'able_to_comment': form.able_to_comment.data,
                   'author_id': current_user.id}
        new_article = Article.create(payload)
        return redirect(url_for('.article_detail', id=new_article.id))
    context = {'legend': 'Создание статьи'}
    return render_template('create-article.html', context=context, form=form)


@main.route('/articles/<int:id>/update', methods=['POST', 'GET'])
@login_required
def article_update(id):
    context = {'legend': 'Редактирование статьи'}
    article = Article.query.get_or_404(id)
    if current_user.id == article.author_id:
        if request.method == 'GET':
            form = ArticleEditForm(MultiDict({'title': article.title, 'intro': article.intro, 'text': article.text,
                                              'able_to_comment': article.able_to_comment}))
        else:
            form = ArticleEditForm()
        if form.validate_on_submit():
            payload = {'title': form.title.data,
                       'intro': form.intro.data,
                       'text': form.text.data,
                       'able_to_comment': form.able_to_comment.data}
            article.upd(payload)
            return redirect(url_for('.article_detail', id=article.id))
        else:
            return render_template('article_update.html', context=context, form=form)
    else:
        return abort(403, 'Статью может редактировать только автор')


@main.route("/login", methods=["POST", "GET"])
def login():
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
    return render_template('login.html', context=context, form=form)


@main.route('/authors')
def authors_page():
    authors = User.get_authors()
    context = {'legend': 'Авторы', 'authors': authors}
    return render_template('authors.html', context=context)


@main.route('/prank/<int:id>')
def prank(id):
    flash('Редактировать комментарии нельзя.', 'danger')
    return redirect(url_for('.article_detail', id=id))
