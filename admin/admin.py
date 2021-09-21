import os
import sqlite3
from flask import Blueprint, render_template, url_for, redirect, session, request, flash, g
#from general import db
from flask_login import login_required

from general.classes import Article, User

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

menu = [{'url': '.index', 'title': 'Панель'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listpubs', 'title': 'Список статей'},
        {'url': '.logout', 'title': 'Выйти'}]


def isLogged():
    return True if session.get('admin_logged') else False


def login_admin():
    session['admin_logged'] = 1


def logout_admin():
    session.pop('admin_logged', None)


@admin.before_request
def before_request():
    """Установление соединения с БД перед выполнением запроса"""
    pass
    # global db
    # db = g.get('link_db')
    # print(db, 'db')


@admin.teardown_request
def teardown_request(request):
    pass
    # global db
    # db = None
    # return request


@admin.route('/')
@login_required
def index():
    if not isLogged():
        return redirect(url_for('.login'))

    return render_template('admin/index.html', menu=menu, title='Админ-панель')


@admin.route('/login', methods=["POST", "GET"])
@login_required
def login():
    if isLogged():
        return redirect(url_for('.index'))

    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['psw'] == os.getenv('ADMIN_PSW'):
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")

    return render_template('admin/login.html', title='Админ-панель')


@admin.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    if not isLogged():
        return redirect(url_for('.login'))

    logout_admin()

    return redirect(url_for('index'))


@admin.route('/list-pubs')
@login_required
def listpubs():
    if not isLogged():
        return redirect(url_for('.login'))
    articles = []
    try:
        articles = Article.query.order_by(Article.date.desc()).all()
    except sqlite3.Error as e:
        print("Ошибка получения статей из БД " + str(e))
    return render_template('admin/listpubs.html', title='Список статей', menu=menu, list=articles)


@admin.route('/list-users')
@login_required
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))
    users = []
    try:
        users = User.query.order_by(User.id.desc()).all()
    except sqlite3.Error as e:
        print("Ошибка получения статей из БД " + str(e))
    return render_template('admin/listusers.html', title='Список статей', menu=menu, list=users)