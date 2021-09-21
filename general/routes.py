import os
import sqlite3
from datetime import datetime

from flask import render_template, request, redirect, flash, url_for, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.datastructures import MultiDict
from werkzeug.security import check_password_hash, generate_password_hash

from general import app, db, manager, TIMEZONE, PROFILE_PIC_NAME
from general.classes import User, Article, UserInfo, Comment
from general.forms import LoginForm, RegistrationForm, ArticleCreateForm, ArticleEditForm, UserEditForm, ImageForm, \
    CreateCommentForm
from general.image import scale_image


@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.before_first_request
def before_first_request():
    pass


@app.before_request
def before_request():
    pass


@app.after_request
def after_request(response):
    return response


def sort_authors(list):
    N = len(list)
    for i in range(N-1):
        for j in range(N-i-1):
            if len(list[j][0].articles) < len(list[j+1][0].articles):
                list[j], list[j+1] = list[j+1], list[j]
    return list


def save_image(picture_file):
    picture_ext = '.' + picture_file.filename.split('.')[-1]
    picture_name = PROFILE_PIC_NAME + str(current_user.id) + picture_ext

    sub_path = os.path.join(app.root_path, 'static/temp_pics', picture_name)
    picture_file.save(sub_path)


    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_name)  # Путь для картинки профиля (для отображения в профиле)
    picture_path2 = os.path.join(app.root_path, 'static/other_profile_pics', picture_name)  # Путь для картинки профиля уменьшенной версии (для остального)

    scale_image(sub_path, picture_path, target=True)
    scale_image(sub_path, picture_path2, target=False)

    if os.path.isfile(sub_path):
        os.remove(sub_path)
    else:
        print("File doesn't exists!")

    return picture_name


@app.route('/profile')
@login_required
def profile():
    context = {
        'user_is_authenticated': current_user.is_authenticated,
        'legend': f'Профиль {current_user.login}'
    }
    articles = db.session.query(Article).filter(Article.author_id == current_user.id).all()
    return render_template('profile.html', context=context, articles=articles)


@app.route('/profile/edit', methods=['POST', 'GET'])
@login_required
def profile_edit():
    context = {
        'user_is_authenticated': current_user.is_authenticated,
        'legend': f'Профиль {current_user.login}'
    }

    if request.method == 'GET':
        form = UserEditForm(MultiDict({'first_name': current_user.info[0].first_name,
                                       'last_name': current_user.info[0].last_name,
                                       'about': current_user.info[0].about,
                                       'gender': current_user.info[0].gender
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

        # if user_info is None:
        #     user_info = UserInfo(id=current_user.id)
        #     db.session.add(user_info)
        # print((form.avatar.data.stream.name), 'ЕСЛИ ФАЙЛ ЕСТЬ, ТО НАПИШЕТ ПУТЬ К TMP ЭТОГО ФАЙЛА')

        current_user.info[0].about = about
        current_user.info[0].first_name = first_name
        current_user.info[0].last_name = last_name
        current_user.info[0].gender = gender

        form2.avatar.data = form.avatar.data
        if form2.validate_on_submit():
            picture_name = save_image(form.avatar.data)
            current_user.picture_name = picture_name
        else:
            if form2.avatar.data.stream.name is not None:
                flash('Аватар не соответствует требованиям.', 'danger')
                return render_template('profile_edit.html', context=context, form=form, form2=form2)

            if current_user.picture_name == 'default_male.png' or current_user.picture_name == 'default_female.png':
                if current_user.info[0].gender == 'М':
                    current_user.picture_name = 'default_male.png'
                else:
                    current_user.picture_name = 'default_female.png'

        db.session.commit()
        return redirect(url_for('profile'))

    return render_template('profile_edit.html', context=context, form=form, form2=form2)


@app.route('/profile/<string:login>', methods=['POST', 'GET'])
def profile_with_login(login):
    if current_user.is_authenticated and current_user.login == login:
        return redirect(url_for('profile'))
    user = db.session.query(User).filter_by(login=login).first()
    if user:
        profile_user = User.query.get(user.id)
        articles = db.session.query(Article).filter(Article.author_id == profile_user.id).all()
        context = {'user_is_authenticated': current_user.is_authenticated,
                   'legend': f'Профиль {login}'
                   }
        return render_template('profile_with_login.html',
                               context=context,
                               profile_user=profile_user,
                               articles=articles)
    else:
        return f'Пользователь под логином {login} не найден.'


@app.route('/logout', methods=['POST', 'GET'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    context = {'user_is_authenticated': current_user.is_authenticated, 'legend': 'Регистрация'}
    if current_user.is_authenticated:
        return redirect(url_for('profile'))

    form = RegistrationForm()

    if form.validate_on_submit():
        login = form.username.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        email = form.email.data
        same_login = User.query.filter_by(login=login).all()
        if same_login:
            flash('Имя пользователся занято', 'danger')
            return render_template('register.html', context=context, form=form)
        else:
            hash_pwd = generate_password_hash(password)
            new_user = User(login=login, password=hash_pwd)

            try:
                db.session.add(new_user)
                db.session.commit()
                id = db.session.query(User.id).filter_by(login=login).first()[0]
                user_info = UserInfo(id=id)
                db.session.add(user_info)
                db.session.commit()
                flash(f'Регистрация аккаунт на email {email} успешно завершена. Можете авторизоваться.', 'success')
            except sqlite3.Error as e:
                return f'При регистрации возникла ошибка {e}'
            return redirect(url_for('login_form'))
    return render_template('register.html', context=context, form=form)


@app.route('/')
@app.route('/home')
def index():
    context = {'user_is_authenticated': current_user.is_authenticated, 'legend': 'INDEX'}
    return render_template('index.html', context=context)


@app.route('/posts')
def posts():
    context = {'user_is_authenticated': current_user.is_authenticated, 'legend': 'Статьи'}
    content = db.session.query(Article, User).filter(Article.author_id == User.id).all()
    return render_template('posts.html', content=content, context=context)


@app.route('/posts/<int:id>', methods=['POST', 'GET'])
def post_detail(id):
    form = None
    context = {'user_is_authenticated': current_user.is_authenticated, 'legend': ''}
    article = Article.query.get(id)
    content = db.session.query(Article, User).filter(Article.id == id).filter(Article.author_id == User.id).first()

    if request.method == 'POST':
        if current_user.is_authenticated:
            form = CreateCommentForm()
            if form.validate_on_submit():
                comment = Comment(text=form.text.data, author_id=current_user.id, article_id=id, date=datetime.now(TIMEZONE))
                db.session.add(comment)
                db.session.commit()
                return redirect(url_for('post_detail', id=id))
        else:
            session['next'] = url_for('post_detail', id=id)
            return redirect(url_for('login_form'))

    return render_template('post_detail.html', content=content, context=context, form=form)


@app.route('/posts/<int:id>/del')
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


@app.route('/comment/<int:id>/del')
@login_required
def comment_delete(id):
    comment = Comment.query.get_or_404(id)
    if current_user.id == comment.author_id:
        try:
            db.session.delete(comment)
            db.session.commit()
            return redirect(url_for('post_detail', id=comment.article_id))
        except:
            return 'При удалении комментария произошла ошибка'
    else:
        return 'Комментарий может удалять только автор'


@app.route('/create-article', methods=['POST', 'GET'])
@login_required
def create_article():
    context = {'user_is_authenticated': current_user.is_authenticated, 'legend': 'Создание статьи'}

    form = ArticleCreateForm()

    if form.validate_on_submit():
        title = form.title.data
        intro = form.intro.data
        text = form.text.data
        able_to_comment = form.able_to_comment.data
        article = Article(title=title, intro=intro, text=text, able_to_comment=able_to_comment, author_id=current_user.id)
        try:
            db.session.add(article)
            db.session.commit()
            return redirect('/posts')
        except:
            return 'При добавлении статьи возникла ошибка'
    return render_template('create-article.html', context=context, form=form)


@app.route('/posts/<int:id>/update', methods=['POST', 'GET'])
@login_required
def post_update(id):
    context = {'user_is_authenticated': current_user.is_authenticated, 'legend': 'Редактирование статьи'}

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


@app.route("/login_form", methods=["POST", "GET"])
def login_form():
    context = {'user_is_authenticated': current_user.is_authenticated, 'legend': 'Авторизация'}
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        login = form.username.data
        password = form.password.data
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            rm = form.remember.data
            login_user(user, remember=rm)
            next = session.pop('next', None)
            return redirect(request.args.get("next") or next or url_for("index"))
        else:
            flash('Неверный логин или пароль', category='danger')
    return render_template('login_form.html', context=context, form=form)


@app.route('/authors', methods=["POST", "GET"])
def authors_page():
    authors = db.session.query(User, UserInfo).filter(User.id == UserInfo.id).all()
    context = {'user_is_authenticated': current_user.is_authenticated,
               'legend': 'Авторы'
               }
    authors = sort_authors(authors)
    return render_template('authors.html', context=context, authors=authors)


@app.route('/prank/<int:id>')
def prank(id):
    flash('Редачить комменты пока нельзя =(((((', 'danger')
    return redirect(url_for('post_detail', id=id))


